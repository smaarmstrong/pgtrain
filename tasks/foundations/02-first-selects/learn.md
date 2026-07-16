THE IDEA

  A table is a grid. Each ROW is one thing (here: one snack in a vending
  machine); each COLUMN is one fact about it (its name, its price). A QUERY
  is a question you ask of that grid, and `SELECT` is the word every question
  starts with. Its smallest complete form:

      SELECT <which columns>
      FROM   <which table>;

  That's it — what you want, where from, semicolon. The server answers with
  a new grid: only the columns you asked for, one row per matching row.

---

  Start with everything. `*` is shorthand for "every column":

```run
SELECT * FROM snacks;
```

  Read the answer top to bottom: the header line is the column names, each
  line below is one row, and the `(6 rows)` footer counts them. Six snacks,
  four facts each.

---

WHY IT MATTERS

  Every dashboard number, every report, every "how many users signed up?"
  is a SELECT underneath. Everything you'll ever add — filtering, joining,
  grouping — is bolted onto this same two-line skeleton. Get the skeleton
  into your fingers and the rest of the trainer is just growing it.

---

CHOOSING COLUMNS

  `*` is for looking around. Real questions name their columns — you get
  ONLY those, IN THE ORDER you list them:

```run
SELECT name FROM snacks;
```

  One column, six rows. Now two columns — and notice the order you write is
  the order you get:

```run
SELECT price, name FROM snacks;
```

  price first, name second, because that's what we asked for. Swap them in
  your head before moving on: `SELECT name, price` would flip the output.

---

JUST A FEW ROWS, PLEASE

  Real tables have millions of rows; you rarely want them all scrolling
  past. `LIMIT n` cuts the answer off after n rows:

```run
SELECT * FROM snacks LIMIT 3;
```

  One honest warning: without an ORDER BY (a later lesson), the server
  hands back rows in whatever order is convenient for it — so `LIMIT 3`
  means "any three", not "the top three". For peeking at a big table,
  that's exactly what you want.

---

GOTCHAS

  - The semicolon ends the statement. Without it psql just waits, showing
    a `-#` continuation prompt.
  - Column ORDER in your SELECT is the order of the output — `name, price`
    and `price, name` are different answers.
  - `*` is great for exploring, but name your columns when it matters:
    the answer shouldn't change shape just because someone adds a column
    to the table later.
  - `LIMIT` without `ORDER BY` gives you an arbitrary handful, not the
    first or best rows.

YOUR TURN

  The task: in `solution.sql`, return the **name** and **price** of every
  snack — those two columns, in that order, nothing else. Pure column
  picking; no filtering needed.
