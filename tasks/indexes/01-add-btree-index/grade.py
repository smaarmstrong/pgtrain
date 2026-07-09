#!/usr/bin/env python3
"""End-state grader: a point lookup on events.token must use an index scan."""
from pgtrain_grader import Grader

g = Grader()
probe = "SELECT * FROM events WHERE token = 'tok-4242'"

# Fresh planner statistics so the plan shape is deterministic.
g.analyze("events")

g.check(
    "an index covering events(token) exists",
    g.exists(
        "SELECT 1 FROM pg_indexes "
        "WHERE tablename = 'events' AND indexdef ILIKE '%(token%'"
    ),
)
g.check(
    "the token lookup no longer sequentially scans the table",
    not g.uses_seqscan(probe),
)
g.check(
    "the token lookup is satisfied by an index scan",
    g.uses_index(probe),
)

g.summary()
