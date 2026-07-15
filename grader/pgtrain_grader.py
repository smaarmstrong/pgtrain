"""Helpers for task graders.

Two audiences:

* state tasks ship a plain-script ``grade.py`` that talks to Postgres through
  ``docker exec ... psql`` (no driver, no venv). They build a ``Grader`` and
  call ``check(...)`` / ``check_error(...)``, then ``g.summary()`` which exits
  0 (all passed) or 1.

* app tasks ship a pytest ``test_grade.py``. They import the learner's code
  from the workspace (``load_module``) and connect to the same Docker Postgres
  via ``dsn()`` / ``sqlalchemy_url()``.

Both learn *where* to connect from the environment the runner sets:
``PGTRAIN_DB``, ``PGTRAIN_CONTAINER``, ``PGTRAIN_DSN``, ``PGTRAIN_WS``. Graders
must never hard-code a database name — the selftest points them at throwaway
databases.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

CONTAINER = os.environ.get("PGTRAIN_CONTAINER", "pgtrain-pg")
PGUSER = "postgres"
# A NULL display sentinel that is printable — a real NUL byte can't be a
# subprocess argument (psql -P null=...), and is unlikely to collide with data.
_NULL = "__PGNULL__"


# ============================================================================
# state-task grading: a real Postgres reached over `docker exec psql`
# ============================================================================
class SQLError(RuntimeError):
    pass


class Grader:
    """End-state assertions against the live task database.

    Never inspects the learner's SQL — only the resulting catalog/plan/behaviour.
    """

    def __init__(self, db: str | None = None):
        self.db = db or os.environ.get("PGTRAIN_DB")
        if not self.db:
            print("PGTRAIN_DB is not set — run graders via `pgtrain check` or selftest.py",
                  file=sys.stderr)
            sys.exit(2)
        self._pass = 0
        self._fail = 0

    # ---- raw access --------------------------------------------------------
    def _psql(self, sql: str, args=()) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["docker", "exec", "-i", CONTAINER, "psql", "-U", PGUSER, "-d", self.db,
             "-v", "ON_ERROR_STOP=1", *args, "-c", sql],
            capture_output=True, text=True, stdin=subprocess.DEVNULL,
        )

    def run(self, sql: str) -> None:
        """Execute SQL (DDL/DML); raise SQLError on failure."""
        r = self._psql(sql)
        if r.returncode != 0:
            raise SQLError(r.stderr.strip())

    def rows(self, sql: str) -> list[tuple]:
        """Return result rows as tuples of strings (NULL -> None)."""
        r = self._psql(sql, args=("-tA", "-F", "\x1f", "-P", "null=" + _NULL))
        if r.returncode != 0:
            raise SQLError(r.stderr.strip())
        out = []
        for line in r.stdout.split("\n"):
            if line == "":
                continue
            out.append(tuple(None if c == _NULL else c for c in line.split("\x1f")))
        return out

    def scalar(self, sql: str):
        rs = self.rows(sql)
        if not rs or not rs[0]:
            return None
        return rs[0][0]

    def exists(self, sql: str) -> bool:
        """True if the query returns at least one row."""
        return bool(self.rows(sql))

    # ---- EXPLAIN plan shape ------------------------------------------------
    def analyze(self, table: str | None = None) -> None:
        self.run(f"ANALYZE {table}" if table else "ANALYZE")

    def plan(self, sql: str) -> dict:
        """Return the top plan node of EXPLAIN (FORMAT JSON) for sql."""
        r = self._psql(f"EXPLAIN (FORMAT JSON) {sql}", args=("-tA",))
        if r.returncode != 0:
            raise SQLError(r.stderr.strip())
        return json.loads(r.stdout)[0]["Plan"]

    @staticmethod
    def node_types(plan: dict) -> list[str]:
        seen = []
        stack = [plan]
        while stack:
            node = stack.pop()
            seen.append(node.get("Node Type", ""))
            stack.extend(node.get("Plans", []))
        return seen

    def uses_index(self, sql: str) -> bool:
        idx = {"Index Scan", "Index Only Scan", "Bitmap Index Scan", "Bitmap Heap Scan"}
        return bool(idx & set(self.node_types(self.plan(sql))))

    def uses_seqscan(self, sql: str) -> bool:
        return "Seq Scan" in self.node_types(self.plan(sql))

    # ---- assertions --------------------------------------------------------
    def check(self, desc: str, cond: bool) -> bool:
        self._tick(desc, bool(cond))
        return bool(cond)

    def check_query(self, desc: str, sql: str) -> bool:
        """Pass if the query returns at least one row."""
        try:
            ok = self.exists(sql)
        except SQLError as e:
            self._tick(desc, False, str(e))
            return False
        self._tick(desc, ok)
        return ok

    def check_error(self, desc: str, sql: str) -> bool:
        """Pass if the SQL *fails* (probing a constraint/trigger that must reject)."""
        r = self._psql(sql)
        ok = r.returncode != 0
        self._tick(desc, ok, "" if ok else "statement unexpectedly succeeded")
        return ok

    def _tick(self, desc, ok, note=""):
        if ok:
            self._pass += 1
            print(f"  \033[32m✓\033[0m {desc}")
        else:
            self._fail += 1
            print(f"  \033[31m✗\033[0m {desc}" + (f"  ({note})" if note else ""))

    def summary(self):
        total = self._pass + self._fail
        if self._fail == 0 and total:
            print(f"\n\033[1;32mPASS\033[0m — {self._pass}/{total} checks")
            sys.exit(0)
        print(f"\n\033[1;31mFAIL\033[0m — {self._pass}/{total} checks")
        sys.exit(1)


# ============================================================================
# app-task grading: connect from the host venv to the Docker Postgres
# ============================================================================
def dsn() -> str:
    d = os.environ.get("PGTRAIN_DSN")
    if not d:
        raise RuntimeError("PGTRAIN_DSN is not set — run via `pgtrain check` or selftest.py")
    return d


def sqlalchemy_url(driver: str = "psycopg") -> str:
    """DSN as a SQLAlchemy URL, e.g. postgresql+psycopg://..."""
    return dsn().replace("postgresql://", f"postgresql+{driver}://", 1)


def workspace() -> Path:
    ws = os.environ.get("PGTRAIN_WS")
    if not ws:
        import pytest
        pytest.fail("PGTRAIN_WS is not set — run via `pgtrain check` or selftest.py")
    return Path(ws)


def load_module(filename: str = "solution.py", module_name: str = "solution"):
    """Import the learner's file from the workspace (never the reference)."""
    import pytest
    path = workspace() / filename
    if not path.exists():
        pytest.fail(f"{filename} not found in your workspace — did you run `pgtrain start`?")
    unique = f"_pgtrain_{module_name}_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(unique, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[unique] = mod
    ws = str(workspace())
    if ws not in sys.path:
        sys.path.insert(0, ws)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001 — learner code can raise anything
        pytest.fail(f"importing your {filename} raised {type(e).__name__}: {e}")
    return mod


def get_attr(mod, name: str):
    import pytest
    obj = getattr(mod, name, None)
    if obj is None:
        pytest.fail(f"your solution must define `{name}` (see the prompt)")
    return obj
