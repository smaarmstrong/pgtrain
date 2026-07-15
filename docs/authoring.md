# Authoring pgtrain tasks

A task is a directory `tasks/<domain>/<nn-name>/`. The domain must appear in
[objectives.md](objectives.md); `<nn-name>` is a zero-padded order prefix plus a
short slug (e.g. `03-left-outer-join`).

Every task has:

| file | required for | purpose |
|------|--------------|---------|
| `meta.json` | all | metadata (below) |
| `prompt.md` | all | what the learner must do |
| `seed.sql` | all | deterministic fixtures, applied to a fresh DB |
| `solution.sql` or `solution/` | all | reference answer (see per-kind) |
| `starter.sql` / `starter/` | optional | scaffold copied into the workspace |
| `grade.py` | `state` | end-state assertions |
| `test_grade.py` | `app` | pytest grader |

## meta.json

```json
{
  "title": "Human title",
  "domain": "indexes",
  "objective": "copy the wording from objectives.md verbatim",
  "kind": "query | state | app",
  "difficulty": 1,          // 1..5, drives XP (10/15/25/40/60)
  "est_min": 10,
  "deps": ["sqlalchemy", "psycopg[binary]"],  // app tasks only
  "ordered": false,         // query tasks: true if the task mandates ORDER BY
  "tags": ["advanced"]      // optional
}
```

## The three kinds

### `kind: query`
The learner writes a single `SELECT` in `workspace/<id>/solution.sql`. The
runner runs it and `solution.sql` (the reference) against a **freshly seeded**
throwaway database and compares result sets:

- order-insensitive **unless** `"ordered": true` (task mandates `ORDER BY`);
- values normalised (numeric `3` == `3.00`, `NULL` distinguished);
- **column names ignored** — only the column *order* and values matter;
- column count must match.

Give a `starter.sql` that is deliberately wrong (so the selftest sees it fail).
The reference must be a single statement (a trailing `;` is fine).

### `kind: state`
The learner mutates the live task database interactively (`pgtrain psql <id>`).
`grade.py` asserts the **end state** and must never read SQL text. It imports
the `Grader` helper:

```python
from pgtrain_grader import Grader
g = Grader()                       # connects to $PGTRAIN_DB via docker exec
g.analyze("mytable")               # fresh planner stats before EXPLAIN checks
g.check("an index exists", g.exists("SELECT 1 FROM pg_indexes WHERE ..."))
g.check("plan uses an index", g.uses_index("SELECT ... WHERE ..."))
g.check_error("the CHECK rejects bad rows", "INSERT INTO ... VALUES (-1)")
g.summary()                        # prints PASS/FAIL and exits 0/1
```

Assert via the catalogs (`information_schema`, `pg_indexes`, `pg_constraint`,
`pg_roles`, `pg_policies`, `pg_matviews`, ...), `EXPLAIN (FORMAT JSON)` plan
*shape* (`g.uses_index` / `g.uses_seqscan` / `g.node_types(g.plan(sql))`), and
behaviour probes (`check_error` for constraints/triggers that must reject).

`solution.sql` (or a `solution/` dir of `*.sql`) must, applied to a freshly
seeded DB, reach the graded end state. The grader must FAIL on the untouched
seed and PASS after the solution — the selftest enforces exactly this.

### `kind: app`
The learner edits Python in `workspace/<id>/`. Ship a `starter/` dir (copied in
on `start`) and a `solution/` dir (the reference). `test_grade.py` is pytest and
connects to the live, freshly-seeded database:

```python
from pgtrain_grader import dsn, sqlalchemy_url, load_module, get_attr
```

Declare packages in `meta.json` `deps`; the runner builds a cached venv per
dependency set.

## The rule that shapes every grader

End-state / result-set only — **any correct query or code passes, never
style**. Seeds are deterministic. `EXPLAIN` tasks assert plan shape *after
`ANALYZE`*, never wall-clock timings.

## Verify before committing

```
./selftest.py <domain>            # your domain: fail-before / pass-after for every task
./selftest.py                     # the whole catalogue
```

The selftest also hard-errors on any task dir lacking `meta.json`, and reports
per-domain counts against the `(target N)` hints in objectives.md.
