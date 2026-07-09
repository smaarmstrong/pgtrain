#!/usr/bin/env python3
"""
selftest.py — prove every grader is neither too lax nor too strict, against a
REAL throwaway Postgres database (and, for app tasks, a throwaway venv).

For each task:
    grader vs untouched seed/starter   -> expect FAIL   (catches pre-satisfied graders)
    grader vs the reference solution   -> expect PASS   (catches wrong/over-strict graders)

It ALSO guards structure:
    * every directory under tasks/<domain>/ MUST contain a meta.json
      (a meta-less dir is a hard error — silent-skip of empty dirs bit pytrain);
    * per-domain task counts are reported against the targets in
      docs/objectives.md (a shortfall warns, it does not fail).

Usage:
    ./selftest.py                      # every task
    ./selftest.py joins indexes/03-... # specific domains and/or task ids
    ./selftest.py --offline            # skip app tasks (which need pip installs)
    ./selftest.py -j 6                 # grading parallelism (default 4)
"""
import argparse
import importlib.machinery
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent

# Load bin/pgtrain (no .py extension) as a module to reuse its logic.
_loader = importlib.machinery.SourceFileLoader("pgtrain_runner", str(REPO / "bin" / "pgtrain"))
_spec = importlib.util.spec_from_file_location("pgtrain_runner", REPO / "bin" / "pgtrain", loader=_loader)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

GRN, RED, YEL, DIM, BLD = R.GRN, R.RED, R.YEL, R.DIM, R.BLD


def _selftest_db(tid: str, kind_tag: str) -> str:
    import hashlib
    h = hashlib.sha1((tid + kind_tag).encode()).hexdigest()[:10]
    return f"pgtrain_selftest_{h}"


def _seed_text(meta) -> str:
    p = meta["_dir"] / "seed.sql"
    return p.read_text() if p.exists() else ""


# ---- per-kind selftest -----------------------------------------------------
def selftest_query(tid, meta):
    db = _selftest_db(tid, "q")
    problems = []
    R.recreate_seeded(db, _seed_text(meta))
    try:
        reference = (meta["_dir"] / "solution.sql").read_text()
        ref_rows, ref_err = R._fetch_rows(db, reference)
        if ref_err:
            return ["reference solution.sql errors:\n      " + ref_err.replace("\n", "\n      ")]
        ordered = bool(meta.get("ordered", False))

        starter = meta["_dir"] / "starter.sql"
        stub_sql = starter.read_text() if starter.exists() else "SELECT 'PGTRAIN_STUB'"
        stub_rows, stub_err = R._fetch_rows(db, stub_sql)
        if stub_err is None:
            ok, _ = R.compare_result_sets(stub_rows, ref_rows, ordered)
            if ok:
                problems.append("grader PASSES on the untouched starter (too lax)")

        ok, msg = R.compare_result_sets(ref_rows, ref_rows, ordered)
        if not ok:
            problems.append("grader FAILS comparing the reference to itself: " + msg)
    finally:
        R.drop_db(db)
    return problems


def selftest_state(tid, meta):
    db = _selftest_db(tid, "s")
    problems = []
    grade_py = meta["_dir"] / "grade.py"
    # negative: untouched seed
    R.recreate_seeded(db, _seed_text(meta))
    try:
        neg = R._run_state_grader(grade_py, db)
        if neg.returncode == 0:
            problems.append("grader PASSES on the untouched seed (too lax)")
        # positive: apply the reference solution
        sol = meta["_dir"] / "solution.sql"
        sol_dir = meta["_dir"] / "solution"
        if sol.exists():
            res = R.psql_script(sol.read_text(), db)
            if res.returncode != 0:
                return ["reference solution.sql failed to apply:\n      "
                        + res.stderr.strip().replace("\n", "\n      ")]
        elif sol_dir.is_dir():
            for f in sorted(sol_dir.glob("*.sql")):
                R.psql_script(f.read_text(), db)
        pos = R._run_state_grader(grade_py, db)
        if pos.returncode != 0:
            tail = "\n".join((pos.stdout + pos.stderr).strip().splitlines()[-6:])
            problems.append("grader FAILS after the reference solution (too strict/wrong):\n"
                            + "\n".join("      " + l for l in tail.splitlines()))
    finally:
        R.drop_db(db)
    return problems


def _make_ws(meta, kind: str) -> Path:
    ws = Path(tempfile.mkdtemp(prefix=f"pgtrain-selftest-{kind}-"))
    src = meta["_dir"]
    if kind == "solution":
        sol_dir = src / "solution"
        if sol_dir.is_dir():
            shutil.copytree(sol_dir, ws, dirs_exist_ok=True)
        else:
            shutil.copy(src / "solution.py", ws / "solution.py")
    else:
        starter_dir = src / "starter"
        if starter_dir.is_dir():
            shutil.copytree(starter_dir, ws, dirs_exist_ok=True)
        elif (src / "starter.py").exists():
            shutil.copy(src / "starter.py", ws / "solution.py")
        else:
            (ws / "solution.py").write_text('"""stub"""\n')
    return ws


def selftest_app(tid, meta):
    db = _selftest_db(tid, "a")
    problems = []
    ws = _make_ws(meta, "stub")
    try:
        R.recreate_seeded(db, _seed_text(meta))
        rc, note, _ = R.run_app_pytest(meta, ws, db)
        if note:
            return ["SKIPPED: " + note.splitlines()[0]]
        if rc == 0:
            problems.append("grader PASSES on the starter stub (too lax)")
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    ws = _make_ws(meta, "solution")
    try:
        R.recreate_seeded(db, _seed_text(meta))
        rc, note, out = R.run_app_pytest(meta, ws, db)
        if rc != 0:
            tail = "\n".join(out.strip().splitlines()[-6:])
            problems.append("grader FAILS on the reference solution (too strict/wrong):\n"
                            + "\n".join("      " + l for l in tail.splitlines()))
    finally:
        shutil.rmtree(ws, ignore_errors=True)
        R.drop_db(db)
    return problems


KIND_FN = {"query": selftest_query, "state": selftest_state, "app": selftest_app}


def selftest_one(tid, meta):
    try:
        problems = KIND_FN[meta["kind"]](tid, meta)
    except Exception as e:  # noqa: BLE001
        problems = [f"selftest crashed: {type(e).__name__}: {e}"]
    if problems and problems[0].startswith("SKIPPED"):
        return tid, "skip", problems[0][9:]
    if problems:
        head = "; ".join(p.splitlines()[0] for p in problems)
        detail = "\n" + "\n".join(problems[-1].splitlines()[1:]) if "\n" in problems[-1] else ""
        return tid, "fail", head + detail
    return tid, "ok", ""


# ---- structure / coverage guards -------------------------------------------
def structural_errors():
    """Hard errors: any task dir lacking meta.json."""
    errs = []
    if not R.TASKS.is_dir():
        return ["tasks/ directory is missing"]
    for dom in sorted(p for p in R.TASKS.iterdir() if p.is_dir()):
        for d in sorted(p for p in dom.iterdir() if p.is_dir()):
            if not (d / "meta.json").exists():
                errs.append(f"{dom.name}/{d.name} has no meta.json (silent-skip guard)")
    return errs


def coverage_report(tasks):
    """Report per-domain counts against docs/objectives.md 'target N' hints."""
    targets = {}
    obj = REPO / "docs" / "objectives.md"
    if obj.exists():
        for line in obj.read_text().splitlines():
            m = re.match(r"^##\s+([a-z0-9-]+)\b.*?target\D*(\d+)", line, re.I)
            if m:
                targets[m.group(1)] = int(m.group(2))
    counts = {}
    for tid in tasks:
        counts[tid.split("/")[0]] = counts.get(tid.split("/")[0], 0) + 1
    print(BLD("\ncoverage vs docs/objectives.md"))
    short = []
    for dom in sorted(set(counts) | set(targets)):
        have, want = counts.get(dom, 0), targets.get(dom)
        tag = ""
        if want is not None and have < want:
            tag = YEL(f"  (target {want} — short by {want - have})")
            short.append(dom)
        elif want is not None:
            tag = DIM(f"  (target {want} ✓)")
        print(f"  {dom:<18} {have}{tag}")
    if short:
        print(DIM(f"note: {len(short)} domain(s) below target — expected while content is in progress"))


# ---- main ------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("selectors", nargs="*", help="task ids and/or domain names")
    ap.add_argument("--offline", action="store_true", help="skip app tasks (need pip installs)")
    ap.add_argument("-j", type=int, default=4, help="parallel graders (default 4)")
    args = ap.parse_args()

    errs = structural_errors()
    if errs:
        for e in errs:
            print(f"  {RED('✗')} {e}")
        print(RED("structural errors — fix these first"))
        sys.exit(1)

    tasks = R.discover()
    if not tasks:
        print("no tasks found"); sys.exit(1)
    all_tasks = dict(tasks)

    if args.selectors:
        chosen = {}
        for sel in args.selectors:
            hits = {t: m for t, m in tasks.items() if t == sel or t.split("/")[0] == sel}
            if not hits:
                r = R.resolve(tasks, sel)
                hits = {r: tasks[r]}
            chosen.update(hits)
        tasks = chosen
    if args.offline:
        skipped = [t for t, m in tasks.items() if m["kind"] == "app"]
        tasks = {t: m for t, m in tasks.items() if m["kind"] != "app"}
        if skipped:
            print(DIM(f"--offline: skipping {len(skipped)} app task(s)"))

    R.ensure_up()

    # Pre-provision each unique app dep-set once, serially, so parallel host-venv
    # grading can't race an install. In the VPN container-fallback path the venv
    # lives in a shared volume and is guarded by flock, so this isn't needed.
    if R.host_data_ok():
        dep_sets = {tuple(sorted(m.get("deps", []))) for m in tasks.values() if m["kind"] == "app"}
        for ds in sorted(dep_sets):
            R.venv_for(list(ds))

    ok = fail = skip = 0
    failed = []
    with ThreadPoolExecutor(max_workers=args.j) as pool:
        for tid, verdict, detail in pool.map(lambda kv: selftest_one(*kv), sorted(tasks.items())):
            if verdict == "ok":
                print(f"  {GRN('✓')} {tid}"); ok += 1
            elif verdict == "skip":
                print(f"  {YEL('~')} {tid} {DIM(detail)}"); skip += 1
            else:
                print(f"  {RED('✗')} {tid}\n    {detail}"); fail += 1; failed.append(tid)

    coverage_report(all_tasks)
    print("----")
    print(f"verified: {ok}   problems: {fail}   skipped: {skip}")
    if failed:
        print("failed: " + " ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
