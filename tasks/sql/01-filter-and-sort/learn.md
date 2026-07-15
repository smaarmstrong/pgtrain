THE IDEA

  A table is a grid: rows are records, columns are fields. The `employees`
  table has one row per person, with columns id, name, department, salary.

  To read from a table you write a SELECT. Its simplest form is:

      SELECT <which columns>
      FROM   <which table>;

  `*` means "every column". Let's look at the whole table first so you can see
  what you're working with. (These snippets run against the real practice
  database — press Enter to run each one and watch the output.)

```run
SELECT * FROM employees;
```

  Seven people, four columns. Every query below just narrows this down.

---

WHY IT MATTERS

  You almost never want the whole table. Real questions are "which orders
  shipped late?", "which users signed up this week?" — a subset of rows, and
  usually only a few columns. Two clauses do that narrowing:

      SELECT name, salary   -- pick COLUMNS (drop the ones you don't need)
      FROM employees
      WHERE ...             -- pick ROWS   (keep only those that match)

  Get comfortable with WHERE and you can answer most day-to-day questions.

---

  First, choosing columns. Instead of `*`, list the ones you want, in the
  order you want them. This asks for just name and salary:

```run
SELECT name, salary FROM employees;
```

  Same seven rows, but only the two columns you named — and in that order.

---

THE WHERE CLAUSE

  `WHERE` keeps only the rows for which a condition is true. The condition is
  written with comparison operators:

      =      equal to            (note: ONE equals sign in SQL, not ==)
      <>     not equal to
      >  <   greater / less than
      >= <=  greater-or-equal / less-or-equal

  Text values go in 'single quotes'. Numbers are written bare. Let's keep only
  the people in the Engineering department:

```run
SELECT name, department FROM employees
WHERE department = 'Engineering';
```

  Five rows come back instead of seven — Dara (Sales) and Faisal (Support)
  were filtered out.

---

  Now a numeric comparison. Note `>` is STRICT — it does not include the
  boundary value itself. Watch what happens to someone sitting exactly on the
  line: Evie earns exactly 60000.

```run
SELECT name, salary FROM employees
WHERE salary > 60000;
```

  Evie (60000) is NOT in the result, because 60000 is not greater than 60000.
  If you wanted to include her you would write `>= 60000`. This boundary is the
  single most common place people get a filter subtly wrong.

---

COMBINING CONDITIONS WITH AND

  Real filters usually have more than one condition. `AND` keeps a row only
  when BOTH sides are true; `OR` keeps it when either is. Putting the two
  conditions together — Engineering people earning strictly more than 60000:

```run
SELECT name, salary FROM employees
WHERE department = 'Engineering'
  AND salary > 60000;
```

  That is exactly what the task asks for. Ada, Chen and Gwen qualify; Bjorn
  (58000) and Evie (exactly 60000) do not, and the non-Engineering rows are
  gone too. Three rows.

---

CHECK IT WORKED

  Your job is to put those two columns and two conditions into `solution.sql`.
  The grader runs your query and the reference against the same seeded data and
  compares the RESULT SETS — the actual rows returned. So:

    - it must return two columns, name then salary (SELECT name, salary);
    - it must return only the three qualifying rows;
    - row ORDER does not matter for this task, so no ORDER BY is needed.

  Any query that produces those rows passes — there's no single "right" text.

---

GOTCHAS

  - Equality is a SINGLE `=` in SQL (department = 'Engineering'), not `==`.
  - Quote text ('Engineering'), leave numbers bare (60000). 'Engineering' is
    also case-sensitive — it must match the data exactly.
  - `>` excludes the boundary; `>=` includes it. The task says "strictly
    greater", so use `>` and Evie's 60000 must be left out.
  - Column ORDER in SELECT is the order you'll get back — ask for name first,
    then salary, to match the spec.
  - End the statement with a single `;` — it must be one statement.
