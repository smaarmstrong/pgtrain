# pgtrain

A console trainer for the whole of PostgreSQL — from SQL craft to production
admin, with a DevOps slant. Same DNA as
[smaarmstrong/redhat](https://github.com/smaarmstrong/redhat) and
[smaarmstrong/pytrain](https://github.com/smaarmstrong/pytrain): a console
runner, task directories, XP + streak, state under `~/.local/state`, and a
selftest that proves every grader **fails before / passes after**.

The difference: every task is graded against a **real Postgres running in
Docker** — never against SQL text. Any correct query, any correct end state,
any correct code passes.

```
git clone https://github.com/smaarmstrong/pgtrain
cd pgtrain
./bin/pgtrain list                          # all tasks, grouped by domain
./bin/pgtrain start sql/01-filter-and-sort  # seed a fresh DB and show the spec
$EDITOR workspace/sql/01-filter-and-sort/solution.sql
./bin/pgtrain check sql/01-filter-and-sort  # grade against real Postgres
```

The only hard requirement is **Docker**. The runner is Python ≥ 3.11, standard
library only. SQL and state tasks reach Postgres through `docker exec ... psql`
— no host `psql`, no driver. App-integration tasks additionally provision a
cached Python venv (uv if present, else venv + pip).

## Commands

| command | what it does |
|---|---|
| `pgtrain list [domain]` | tasks grouped by domain, with your status |
| `pgtrain start <id>` | create the task's database (+ workspace) and show the spec |
| `pgtrain psql <id>` | open an interactive `psql` shell on the task database |
| `pgtrain check <id>` | grade your work |
| `pgtrain solution <id>` | reveal a reference solution |
| `pgtrain reset <id>` | drop & recreate the task database (and reset workspace files) |
| `pgtrain status` | XP, daily streak, per-domain progress bars |
| `pgtrain up` / `down` | start / stop the shared container |
| `pgtrain gc` | drop every `pgtrain_*` database (frees space; safe) |
| `pgtrain nuke` | remove the container entirely (destroys all task data) |
| `pgtrain doctor` | container / database health |

`<id>` is `domain/nn-name`, or just the unique trailing name. Progress lives in
`~/.local/state/pgtrain/progress.json`; XP scales with difficulty and the streak
counts consecutive days with at least one pass.

## Task kinds

- **query** — you write a `SELECT` in `solution.sql`. The grader runs it and the
  reference against the seeded database and compares **result sets** —
  order-insensitive unless the task mandates `ORDER BY`, values/NULLs
  normalised, column names ignored. Any correct query passes.
- **state** — you apply DDL/DML/admin changes with `pgtrain psql`. The grader
  asserts the **end state** via the system catalogs, `EXPLAIN` plan shape (after
  `ANALYZE`), and behaviour probes. It never reads your SQL.
- **app** — you edit Python (SQLAlchemy, Alembic, asyncpg, FastAPI …). The
  grader runs **pytest in a venv** against the same Docker Postgres.

## Domains

`foundations` · `sql` · `joins` · `aggregation` · `subqueries` · `datatypes` ·
`ddl` · `indexes` · `txn` · `views` · `plpgsql` · `textsearch` · `security` ·
`admin` · `replication` · `app` · `projects`.

`foundations` comes first in the teaching order: interactive lessons that
teach the ambient tools everything else assumes — what a server/database even
is, psql and its meta-commands, bare `SELECT` mechanics, reading Postgres
errors, and why the Docker sandbox means you can't break anything. Tasks that
lean on a foundations lesson list it as a soft `prereq` in their `meta.json`;
if you haven't passed it yet, `learn`/`train` print a one-line pointer to it —
advisory only, never a gate.

The full coverage checklist is [docs/objectives.md](docs/objectives.md); the
task-authoring guide is [docs/authoring.md](docs/authoring.md).

## Safety model

The runner manages exactly one container, `pgtrain-pg` (`postgres:16`,
auto-started on demand, bound to `127.0.0.1:55432`, with
`pg_stat_statements` preloaded). Every task gets its own database named
`pgtrain_<task>`. **Setup, reset, teardown and GC touch only databases whose
names begin with `pgtrain_` and only the `pgtrain-pg` container** — never a
global drop, never anything unprefixed. `pgtrain gc` and `pgtrain nuke` are the
only destructive commands and both say exactly what they remove.

## How grading works

Each task is a directory of `meta.json`, `prompt.md`, `seed.sql`, a reference
solution, and (for `state`/`app`) a grader. `check` ensures the container is up,
seeds a fresh per-task database, and runs the grader for that kind. Graders
assert behaviour and end state, never style.

## Selftest

```
./selftest.py                 # every task: grader FAILS on the seed, PASSES after the reference
./selftest.py indexes app     # specific domains and/or task ids
./selftest.py --offline       # skip app tasks (which need pip installs)
```

For each task, in a throwaway `pgtrain_selftest_*` database (and a throwaway
workspace/venv for app tasks), the selftest runs the grader against the
untouched seed (expect **FAIL**) and against the reference solution (expect
**PASS**) — catching graders that are too lax or too strict. It also
hard-errors on any task directory missing `meta.json` and reports per-domain
coverage against `docs/objectives.md`.

A devcontainer with docker-in-docker (`.devcontainer/`) runs the whole suite —
SQL, state, and app tasks — in CI.
