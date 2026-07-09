# pgtrain coverage objectives

The source of truth for what the catalogue must teach. Every objective below
becomes at least one task; a task's `meta.json` `objective` copies the wording
verbatim. Advanced/bonus material is tagged `advanced` in `meta.json`.

The header of each domain carries a **`(target N)`** hint — `selftest.py`
counts the task directories per domain against it and reports any shortfall
(a shortfall warns; it never fails the selftest, so content can land in
batches). What *does* fail the selftest is any task directory missing a
`meta.json`.

Grading philosophy: **end-state / result-set only, never SQL text**. Any
correct query or code passes. Seeds are deterministic. `EXPLAIN` tasks assert
plan *shape* after `ANALYZE`, never wall-clock timings. Everything works
offline once `postgres:16` and the venv wheels are cached.

Task kinds: `query` (write a SELECT, result sets compared) · `state` (apply
DDL/DML/admin, end state asserted via catalogs / EXPLAIN / behaviour probes) ·
`app` (edit Python, pytest in a venv against the live database).

---

## sql — SQL fundamentals (target 12)
- [x] `WHERE` predicates: comparison, `AND`/`OR`/`NOT`, boundary conditions
- [ ] `ORDER BY` incl. multiple keys, `ASC`/`DESC`, `NULLS FIRST/LAST`
- [ ] `DISTINCT` and `DISTINCT ON`
- [ ] `LIMIT`/`OFFSET` and keyset pagination
- [ ] `IN`, `BETWEEN`, `LIKE`/`ILIKE` basics
- [ ] `NULL` semantics: `IS NULL`, `COALESCE`, `NULLIF`, three-valued logic
- [ ] `CASE` expressions
- [ ] set operations: `UNION`/`UNION ALL`/`INTERSECT`/`EXCEPT`
- [ ] `INSERT`/`UPDATE`/`DELETE` with `RETURNING`
- [ ] `INSERT ... ON CONFLICT` (upsert)
- [ ] casting and common expression functions
- [ ] `VALUES` lists and derived tables

## joins — joins (target 12)
- [ ] inner join
- [ ] left / right / full outer joins
- [ ] self join
- [ ] anti-join (`NOT EXISTS` / `LEFT JOIN ... IS NULL`)
- [ ] semi-join (`EXISTS` / `IN`)
- [ ] multi-table joins and join order
- [ ] join on inequality / range conditions
- [ ] `USING` and natural join pitfalls
- [ ] `CROSS JOIN` and its uses
- [ ] `LATERAL` join `advanced`
- [ ] correlated lateral for top-N-per-group `advanced`
- [ ] `FULL JOIN` for reconciliation/diffing

## aggregation — aggregation & window functions (target 12)
- [ ] `GROUP BY` with `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`
- [ ] `HAVING`
- [ ] `FILTER (WHERE ...)` on aggregates
- [ ] `GROUPING SETS`/`ROLLUP`/`CUBE` `advanced`
- [ ] `array_agg`/`string_agg`/`jsonb_agg` with ordering
- [ ] window: `ROW_NUMBER`/`RANK`/`DENSE_RANK` `advanced`
- [ ] window: `PARTITION BY` + frames `advanced`
- [ ] window: `LAG`/`LEAD` `advanced`
- [ ] window: running totals / moving averages `advanced`
- [ ] `percentile_cont`/`percentile_disc`
- [ ] distinct aggregates
- [ ] combining aggregates with joins

## subqueries — subqueries & CTEs (target 10)
- [ ] scalar subqueries
- [ ] `IN`/`ANY`/`ALL` subqueries
- [ ] correlated subqueries
- [ ] `EXISTS`/`NOT EXISTS`
- [ ] `WITH` common table expressions
- [ ] multiple/chained CTEs
- [ ] recursive CTE: hierarchy walk `advanced`
- [ ] recursive CTE: graph / transitive closure `advanced`
- [ ] data-modifying CTE (`WITH ... AS (INSERT ... RETURNING)`) `advanced`
- [ ] subquery vs join rewrite

## datatypes — data types: arrays, ranges, enums, JSONB (target 12)
- [ ] arrays: literals, `ANY`/`ALL`, `unnest`
- [ ] arrays: containment operators, GIN index `advanced`
- [ ] enums: create and use
- [ ] ranges: `int4range`/`tstzrange`, containment/overlap
- [ ] range exclusion constraint `advanced`
- [ ] JSONB: `->`/`->>`/`#>>` navigation
- [ ] JSONB: containment `@>` and existence `?`
- [ ] JSONB: GIN indexing `advanced`
- [ ] JSONB: `jsonb_set`/`jsonb_build_object`
- [ ] JSONB: `jsonb_path_query` `advanced`
- [ ] `hstore` / composite types
- [ ] `numeric` vs `float` and money handling

## ddl — DDL & constraints (target 12)
- [ ] create tables with appropriate types
- [ ] primary keys and natural vs surrogate
- [ ] foreign keys incl. `ON DELETE`/`ON UPDATE` actions
- [ ] `CHECK` constraints
- [ ] `UNIQUE` constraints incl. partial/expression
- [ ] `NOT NULL` and defaults
- [ ] generated columns (`GENERATED ALWAYS AS ... STORED`)
- [ ] `ALTER TABLE`: add/drop/alter columns safely
- [ ] identity columns / sequences
- [ ] domains and custom constraints
- [ ] declarative partitioning: range `advanced`
- [ ] declarative partitioning: list/hash + pruning `advanced`

## indexes — indexes & performance (target 14)
- [x] btree index for a point lookup (Index Scan vs Seq Scan)
- [ ] composite index and column order
- [ ] covering index (`INCLUDE`) / index-only scan
- [ ] partial index
- [ ] expression index
- [ ] GIN index for arrays / JSONB
- [ ] GiST index for ranges / geometry `advanced`
- [ ] unique index vs unique constraint
- [ ] reading `EXPLAIN`/`EXPLAIN (ANALYZE, BUFFERS)`
- [ ] when an index does NOT help (low selectivity / functions on columns)
- [ ] bitmap heap scan and multiple indexes
- [ ] index bloat and `REINDEX` `advanced`
- [ ] `CREATE INDEX CONCURRENTLY` `advanced`
- [ ] statistics targets / correlated columns `advanced`

## txn — transactions & concurrency (target 12)
- [ ] transaction basics, `BEGIN`/`COMMIT`/`ROLLBACK`, savepoints
- [ ] read committed vs repeatable read visibility
- [ ] serializable isolation and serialization failures `advanced`
- [ ] explicit row locks: `SELECT ... FOR UPDATE`
- [ ] `SELECT ... FOR UPDATE SKIP LOCKED` (work-queue pattern)
- [ ] `NOWAIT` and lock-wait behaviour
- [ ] deadlock: reproduce and reason about it `advanced`
- [ ] lock modes and `pg_locks`
- [ ] advisory locks
- [ ] idempotent upsert under concurrency
- [ ] `LISTEN`/`NOTIFY`
- [ ] MVCC and dead tuples (leads into VACUUM)

## views — views & materialized views (target 10)
- [ ] create and use a view
- [ ] updatable views and `WITH CHECK OPTION`
- [ ] `INSTEAD OF` triggers on views `advanced`
- [ ] materialized views: create and query
- [ ] `REFRESH MATERIALIZED VIEW`
- [ ] `REFRESH ... CONCURRENTLY` and the unique-index requirement `advanced`
- [ ] view vs matview trade-offs
- [ ] dependency tracking / `CREATE OR REPLACE VIEW`
- [ ] security-barrier views
- [ ] composing views for reporting

## plpgsql — functions, triggers & PL/pgSQL (target 12)
- [ ] SQL functions (`LANGUAGE sql`)
- [ ] PL/pgSQL functions: variables, control flow
- [ ] function volatility (`IMMUTABLE`/`STABLE`/`VOLATILE`)
- [ ] returning `SETOF` / `TABLE`
- [ ] `RAISE` and exception handling in PL/pgSQL
- [ ] `BEFORE`/`AFTER` row triggers
- [ ] audit-trail trigger writing to a history table
- [ ] statement-level triggers
- [ ] trigger to maintain a derived/denormalized column
- [ ] `SECURITY DEFINER` functions and `search_path` safety `advanced`
- [ ] `DO` blocks
- [ ] aggregate or window function definition `advanced`

## textsearch — text search & patterns (target 10)
- [ ] `LIKE`/`ILIKE` and escaping
- [ ] `SIMILAR TO`
- [ ] POSIX regex (`~`, `~*`, `regexp_replace`, `regexp_matches`)
- [ ] `pg_trgm` similarity and GIN/GiST trigram index `advanced`
- [ ] full-text: `to_tsvector`/`to_tsquery`
- [ ] full-text: ranking with `ts_rank`
- [ ] full-text: GIN index on a tsvector column
- [ ] full-text: generated `tsvector` column + trigger
- [ ] phrase search and weights `advanced`
- [ ] `citext` / case-insensitive matching

## security — roles, privileges & RLS (target 10)
- [ ] create roles / login roles / group roles
- [ ] `GRANT`/`REVOKE` on tables and schemas
- [ ] default privileges (`ALTER DEFAULT PRIVILEGES`)
- [ ] column-level privileges
- [ ] `SET ROLE` and privilege inheritance
- [ ] row-level security: enable + a `USING` policy
- [ ] RLS: `WITH CHECK` policies for writes
- [ ] RLS: per-tenant isolation policy `advanced`
- [ ] `SECURITY DEFINER` vs `INVOKER` boundary
- [ ] least-privilege application role

## admin — admin & ops (target 14)
- [ ] `VACUUM` and `VACUUM (VERBOSE, ANALYZE)`
- [ ] autovacuum settings per table (`reloptions`)
- [ ] `ANALYZE` and planner statistics
- [ ] detect table/index bloat
- [ ] `pg_stat_activity`: find long-running / idle-in-transaction queries
- [ ] `pg_stat_user_tables`: seq vs index scans, dead tuples
- [ ] `pg_stat_statements`: top queries by total/mean time
- [ ] terminate/cancel a backend safely
- [ ] `pg_dump` a database / table (custom + plain)
- [ ] `pg_restore` into a fresh database
- [ ] key config parameters (`shared_buffers`, `work_mem`, `random_page_cost`)
- [ ] connection limits and `statement_timeout` / `idle_in_transaction_session_timeout`
- [ ] table/database size introspection
- [ ] checkpoints & WAL basics `advanced`

## replication — replication & HA (target 10) `advanced`
- [ ] streaming vs logical replication concepts
- [ ] create a `PUBLICATION`
- [ ] create a `SUBSCRIPTION` (second container)
- [ ] verify logical replication propagates changes
- [ ] replica identity and its effect on updates/deletes
- [ ] publication for a subset of tables/columns
- [ ] monitoring replication lag (`pg_stat_replication`)
- [ ] conflict / failover concepts
- [ ] `pg_basebackup` mechanics
- [ ] synchronous vs asynchronous trade-offs

## app — app integration (target 14)
- [x] SQLAlchemy Core: reflect + aggregate against live Postgres
- [ ] SQLAlchemy Core: parameterized inserts / transactions
- [ ] SQLAlchemy ORM: models, session, relationships
- [ ] SQLAlchemy ORM: query with joins and eager loading
- [ ] Alembic: write a forward migration
- [ ] Alembic: a safe, reversible migration (down works)
- [ ] connection pooling configuration and behaviour
- [ ] psycopg: server-side cursors / `COPY`
- [ ] asyncpg: connect and query asynchronously
- [ ] async FastAPI endpoint backed by asyncpg
- [ ] OSP: apply-once / idempotent migration guard
- [ ] OSP: multi-tenant schema-per-client pattern
- [ ] OSP: detect schema drift between two databases
- [ ] transaction management in an app handler

## projects — composite projects (target 5)
- [ ] design a schema from a written spec (constraints + indexes)
- [ ] optimize a deliberately slow workload (assert the plan improves)
- [ ] build an audit-logging trigger system
- [ ] write and verify a zero-downtime column migration
- [ ] end-to-end: model + migration + query layer
