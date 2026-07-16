#!/usr/bin/env python3
"""End-state grader: the three seeded vault rows survived, and the committed
receipt row exists. (End state only — it cannot see HOW you got here, which is
the point: a rolled-back DELETE leaves no trace.)"""
from pgtrain_grader import Grader

g = Grader()

g.check(
    "the three original vault rows (deed, will, medal) are intact",
    g.scalar(
        "SELECT count(*) FROM vault "
        "WHERE (id, item) IN ((1, 'deed'), (2, 'will'), (3, 'medal'))"
    ) == "3",
)
g.check(
    "your committed receipt row (id 4, item 'receipt') exists",
    g.exists("SELECT 1 FROM vault WHERE id = 4 AND item = 'receipt'"),
)
g.check(
    "the vault holds exactly those four rows",
    g.scalar("SELECT count(*) FROM vault") == "4",
)

g.summary()
