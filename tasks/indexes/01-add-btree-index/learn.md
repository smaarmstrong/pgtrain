THE IDEA

  An index is like the index at the back of a book. Without one, to find every
  page that mentions "vacuum" you'd read the whole book cover to cover. With
  one, you flip to the alphabetical list, find "vacuum", and jump straight to
  the pages. A database index does the same for a column.

  The `events` table has 5,000 rows and the app constantly looks a row up by
  its `token`:

      SELECT * FROM events WHERE token = 'tok-4242';

  Right now there is no index on `token`, so Postgres has to scan all 5,000
  rows every time. Let's prove that, then fix it.

---

WHY IT MATTERS

  "Read the whole table" is fine for 5,000 rows and a disaster for 5,000,000.
  A point lookup (WHERE column = one value) is the bread and butter of every
  application, and an index turns it from "look at everything" into "jump
  straight there". Knowing how to SEE which one Postgres is doing — and how to
  change it — is a core performance skill.

---

READING THE PLAN WITH EXPLAIN

  Before running a query, Postgres builds a *plan*: its strategy for getting
  the rows. You can see that plan without running the query for real by putting
  `EXPLAIN` in front of it. Let's look at the plan for our lookup:

```run
EXPLAIN SELECT * FROM events WHERE token = 'tok-4242';
```

  Read the top line. It says **Seq Scan on events** — a "sequential scan", i.e.
  Postgres will walk the entire table row by row, checking each token. That's
  the whole-book read. There is no faster option available yet, because there
  is no index for it to use.

---

  `EXPLAIN ANALYZE` goes one step further: it actually runs the query and
  reports real timings and how many rows it examined. Watch "rows removed by
  filter" — that's wasted work.

```run
EXPLAIN ANALYZE SELECT * FROM events WHERE token = 'tok-4242';
```

  It found 1 matching row but had to inspect ~5,000 to be sure. That is exactly
  what an index removes.

---

CREATING THE INDEX

  You create an index with `CREATE INDEX`. The shape is:

      CREATE INDEX <name> ON <table> (<column>);

  The name is just a label (pick something descriptive). The default index type
  is a *B-tree*, which is exactly what a `=` lookup wants — no special options
  needed. Let's build one on `token`:

```run
CREATE INDEX events_token_idx ON events (token);
```

  That's it. Postgres has now built the sorted "back-of-book index" for the
  token column.

---

  One more habit: after changing a table, run `ANALYZE` so the planner has
  fresh statistics and will actually choose the new index. (The grader does
  this for you, but it's good practice to know.)

```run
ANALYZE events;
```

---

CHECK IT WORKED

  Look at the plan again — the same command as before, now that the index
  exists:

```run
EXPLAIN SELECT * FROM events WHERE token = 'tok-4242';
```

  The top line should now say **Index Scan using events_token_idx** (or a
  Bitmap Index Scan) instead of Seq Scan. Postgres is jumping straight to the
  row via the index.

  That is exactly what the grader checks: it runs ANALYZE, then inspects the
  EXPLAIN plan and asserts the lookup uses an index scan and no longer does a
  sequential scan. It never reads the SQL you typed — any index that makes the
  lookup use an index scan passes.

  You do your real work in an interactive shell:

      pgtrain psql indexes/01-add-btree-index

  create the index there, then run  pgtrain check indexes/01-add-btree-index.

---

GOTCHAS

  - The index must be on the column you filter by. An index on `id` or
    `payload` won't help a lookup by `token`.
  - A plain B-tree (the default) is right for `=` and range lookups. You do NOT
    need to specify a type or options for this task.
  - Freshly created, on tiny tables, the planner may still prefer a Seq Scan
    because the table is so small the index isn't worth it — that's why we
    ANALYZE, and why this table has 5,000 rows: enough for the index to win.
  - Building an index has a cost (disk space + slower writes). It's a trade you
    make for faster reads on columns you actually search by — not something to
    add to every column blindly.
