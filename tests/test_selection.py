#!/usr/bin/env python3
"""
Lightweight unit tests for the train/learn selection + spaced-repetition logic
in bin/pgtrain. Stdlib only (no pytest, no Docker), so it runs anywhere — it
never starts a container, touches real progress, or reads the real task tree.
It exercises the PURE decision functions on synthetic task/state dicts.

    ./tests/test_selection.py        # prints a line per check, exits nonzero on failure
"""
import importlib.machinery
import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_loader = importlib.machinery.SourceFileLoader("pgtrain_runner", str(REPO / "bin" / "pgtrain"))
_spec = importlib.util.spec_from_file_location("pgtrain_runner", REPO / "bin" / "pgtrain", loader=_loader)
r = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r)

_fails = []
def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        _fails.append(name)

def iso(days_from_today):
    return (date.today() + timedelta(days=days_from_today)).isoformat()

# Synthetic task set spanning three domains in a known teaching order.
TASKS = {
    "sql/01-a":     {"title": "a", "domain": "sql"},
    "sql/02-b":     {"title": "b", "domain": "sql"},
    "indexes/01-c": {"title": "c", "domain": "indexes"},
    "app/01-d":     {"title": "d", "domain": "app"},
}

def blank_state(**over):
    st = {"tasks": {}, "xp": 0, "streak": {"count": 0, "last": ""},
          "current": None, "recent_picks": []}
    st.update(over)
    return st

# ---- spaced-repetition ladder ---------------------------------------------
check("review_interval ladder is 1,3,7,16,35,75",
      [r.review_interval(n) for n in range(1, 7)] == [1, 3, 7, 16, 35, 75])
check("review_interval doubles past the ladder",
      r.review_interval(7) == 150 and r.review_interval(8) == 300)
check("days_overdue: None when unscheduled", r.days_overdue("") is None)
check("days_overdue: 0 when due today", r.days_overdue(iso(0)) == 0)
check("days_overdue: positive when past due", r.days_overdue(iso(-3)) == 3)
check("days_overdue: negative when in the future", r.days_overdue(iso(5)) == -5)

entry = {}
r.schedule_review(entry, 2)
check("schedule_review records reps + a due 3d out (reps=2)",
      entry["reps"] == 2 and entry["due"] == iso(3))

# ---- teaching order (fundamentals first: sql < indexes < app) --------------
check("curriculum_key orders sql < indexes < app",
      sorted(TASKS, key=r.curriculum_key) == ["sql/01-a", "sql/02-b", "indexes/01-c", "app/01-d"])

# ---- next_new: fundamentals first, resumes unfinished ----------------------
st = blank_state()
check("next_new on a clean slate is the first sql task",
      r.next_new(TASKS, st)[0] == "sql/01-a")
st = blank_state(tasks={"sql/01-a": {"passed": True}})
check("next_new skips a passed task",
      r.next_new(TASKS, st)[0] == "sql/02-b")
st = blank_state(tasks={"sql/01-a": {"passed": False, "attempts": 2}})
check("next_new returns an in-progress (attempted, unpassed) task",
      r.next_new(TASKS, st)[0] == "sql/01-a")

# ---- due_reviews -----------------------------------------------------------
st = blank_state(tasks={
    "sql/01-a": {"passed": True, "due": iso(-5)},     # 5d overdue
    "sql/02-b": {"passed": True, "due": iso(-1)},     # 1d overdue
    "indexes/01-c": {"passed": True, "due": iso(10)}, # not yet due
    "app/01-d": {"passed": True},                     # passed, never scheduled
})
due = [tid for tid, _ in r.due_reviews(TASKS, st)]
check("due_reviews excludes not-yet-due tasks", "indexes/01-c" not in due)
check("due_reviews includes an unscheduled passed task", "app/01-d" in due)
check("due_reviews is most-overdue-first", due[0] == "sql/01-a" and due[1] == "sql/02-b")

# ---- choose_task: reviews vs new, and the two-in-a-row wall ----------------
st = blank_state(tasks={"sql/01-a": {"passed": True, "due": iso(-2)}})
tid, meta, kind, reason = r.choose_task(TASKS, st)
check("choose_task prefers a due review", kind == "review" and tid == "sql/01-a")

st = blank_state()
tid, meta, kind, reason = r.choose_task(TASKS, st)
check("choose_task gives new material when nothing is due",
      kind == "new" and tid == "sql/01-a")

# two reviews in a row + new material waiting -> the 3rd pick must be new
st = blank_state(
    tasks={"sql/01-a": {"passed": True, "due": iso(-2)}},   # a review is due
    recent_picks=["review", "review"],                      # ...but two just happened
)
tid, meta, kind, reason = r.choose_task(TASKS, st)
check("choose_task never gives 3 reviews in a row while new work waits",
      kind == "new")

# but if there is NO new material left, a review is fine even after two
st = blank_state(
    tasks={t: {"passed": True, "due": iso(-2)} for t in TASKS},
    recent_picks=["review", "review"],
)
tid, meta, kind, reason = r.choose_task(TASKS, st)
check("choose_task falls back to review when all new material is done",
      kind == "review")

# nothing due, nothing new
st = blank_state(tasks={t: {"passed": True, "due": iso(30)} for t in TASKS})
tid, meta, kind, reason = r.choose_task(TASKS, st)
check("choose_task returns None when caught up", tid is None and kind is None)

# ---- lesson parsing (```run block is SQL, kept verbatim) -------------------
beats = r.parse_lesson("intro line\n---\nmore prose\n```run\nSELECT 1;\nSELECT 2;\n```\ntail")
kinds = [b[0] for b in beats]
check("parse_lesson splits prose / pause / run / prose",
      kinds == ["prose", "pause", "prose", "run", "prose"])
check("parse_lesson keeps a run block verbatim as a list of lines",
      beats[3][1] == ["SELECT 1;", "SELECT 2;"])

print("----")
if _fails:
    print(f"FAILED {len(_fails)}: " + ", ".join(_fails))
    sys.exit(1)
print("all selection/SR checks passed")
