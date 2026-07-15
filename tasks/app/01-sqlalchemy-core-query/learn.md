THE IDEA

  This task is written in Python, but the thing it actually does is a database
  query — so we'll build the query in plain SQL first (you can run it right
  here against the practice database), get it exactly right, and only then
  translate it to SQLAlchemy. SQLAlchemy Core is just a way to write that same
  SQL using Python objects instead of a hand-typed string.

  The `sales` table has one row per sale: a region and an amount.

```run
SELECT * FROM sales;
```

  Six rows across three regions. We want ONE row per region with that region's
  total — a summary.

---

WHY IT MATTERS

  "Total per group" is the single most common report in existence: revenue per
  region, signups per day, errors per service. In SQL that's an *aggregate*
  with GROUP BY. And building queries from Python objects (instead of pasting
  raw SQL strings) is how real apps stay safe from SQL-injection and adapt to
  different databases. Learn this shape once and you reuse it constantly.

---

SUM AND GROUP BY

  `SUM(amount)` adds up a column. On its own it collapses the whole table to a
  single number:

```run
SELECT SUM(amount) FROM sales;
```

  `GROUP BY region` changes that: it splits the rows into one bucket per
  region, and the SUM is computed per bucket. Now we get one row each:

```run
SELECT region, SUM(amount) AS total
FROM sales
GROUP BY region;
```

  Three rows — one per region — each with its own total. The `AS total` just
  gives the summed column a readable name. Rule of thumb: every column in the
  SELECT that isn't inside an aggregate like SUM must appear in GROUP BY.

---

ORDERING THE RESULT

  The task wants the biggest region first, and ties broken alphabetically.
  `ORDER BY` sorts the result; `DESC` means descending (high to low), `ASC`
  means ascending (the default). You can sort by more than one thing — the
  second only breaks ties in the first:

```run
SELECT region, SUM(amount) AS total
FROM sales
GROUP BY region
ORDER BY total DESC, region ASC;
```

  That is the exact result the task expects:  east 200, north 135, south 125.
  This SQL is your target — the Python just has to produce the same thing.

---

THE SAME QUERY IN SQLALCHEMY CORE

  Now the translation. Your function receives a live `engine` (a connection
  factory). SQLAlchemy Core builds the query from Python objects. Each SQL piece
  above has a direct counterpart — read this side by side with the query you
  just ran:

      from sqlalchemy import MetaData, Table, func, select

      md = MetaData()
      # "reflect" = read the existing table's shape from the DB, so you don't
      # redefine its columns by hand:
      sales = Table("sales", md, autoload_with=engine)

      total = func.sum(sales.c.amount).label("total")   # SUM(amount) AS total
      stmt = (
          select(sales.c.region, total)                 # SELECT region, total
          .group_by(sales.c.region)                     # GROUP BY region
          .order_by(total.desc(), sales.c.region.asc()) # ORDER BY total DESC, region ASC
      )

  `sales.c.region` is "the region column of the sales table" — `.c` stands for
  "columns". `func.sum(...)` is how you call any SQL function from Python.

---

  Finally you have to RUN the statement and hand back the rows. Open a
  connection, execute, and turn each row into a plain tuple:

      with engine.connect() as conn:
          return [tuple(row) for row in conn.execute(stmt)]

  `engine.connect()` in a `with` block borrows a connection and returns it
  automatically. Each row from `execute` is already (region, total); wrapping it
  in `tuple(...)` gives the exact `[(region, total), ...]` list the task wants.

---

CHECK IT WORKED

  Put all of that inside `revenue_by_region(engine)` in `solution.py`. The
  grader runs pytest against the same live Postgres and checks the returned
  rows: one tuple per region, totals summed correctly, ordered by total
  descending then region ascending. The total may come back as int, float or
  Decimal — the grader compares numerically, so you don't need to cast it.

      pgtrain start app/01-sqlalchemy-core-query   # sets up the workspace
      $EDITOR workspace/app/01-sqlalchemy-core-query/solution.py
      pgtrain check app/01-sqlalchemy-core-query

---

GOTCHAS

  - Reflect the table (`autoload_with=engine`); don't hand-write a raw SQL
    string, and don't redefine the columns yourself — the task wants Core.
  - Order matters: `.order_by(total.desc(), sales.c.region.asc())` — total
    first, region second to break ties. Swapping them changes the result.
  - Return a list of TUPLES, not SQLAlchemy Row objects — `tuple(row)` does the
    conversion. A list of Rows may look right when printed but isn't equal to
    the expected tuples.
  - `func.sum` (lower-case, from sqlalchemy) — it builds the SQL `SUM()`; it is
    not Python's built-in `sum`.
