# Index a hot lookup column

The `events` table has 5,000 rows:

| column  | type   |
|---------|--------|
| id      | bigint (primary key) |
| token   | text   |
| payload | text   |

The application constantly runs point lookups like:

```sql
SELECT * FROM events WHERE token = 'tok-4242';
```

Right now `token` has no index, so every lookup is a sequential scan of the
whole table. **Create an index** that lets the planner satisfy that lookup with
an index scan instead.

Do your work in an interactive shell:

```
pgtrain psql indexes/01-add-btree-index
```

Then run `pgtrain check indexes/01-add-btree-index`.

> The grader runs `ANALYZE`, then inspects the `EXPLAIN (FORMAT JSON)` plan
> shape — it checks that the lookup uses an index scan and no longer does a
> sequential scan. It never looks at the SQL you typed, so any index that does
> the job passes.
