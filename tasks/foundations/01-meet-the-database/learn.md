THE IDEA

  Before any SQL, get clear on WHAT you are talking to.

  PostgreSQL is a SERVER: a program that runs all the time, holds data on
  disk, and answers questions sent to it. You never touch the data directly —
  you send requests to the server and it replies.

  To send those requests you use a CLIENT. Ours is `psql`, the standard
  Postgres terminal client: you type a command, it ships it to the server,
  and prints whatever comes back. Server and client are separate programs —
  a point that matters later, because errors, permissions and performance can
  come from either side.

---

WHERE OUR SERVER LIVES

  In this trainer the server runs inside a Docker CONTAINER called
  `pgtrain-pg` — think of it as a sealed, disposable box on your machine with
  a whole Postgres inside. You don't need to install anything, and nothing
  you do inside it can touch your real system. (A later lesson leans into
  just how safe that makes you.)

  One server holds MANY databases — separate, named collections of tables
  that don't see each other. pgtrain gives every task its own database named
  `pgtrain_<task>`, so experiments in one task can never contaminate another.

  Let's ask the server which database this lesson is connected to. This is
  SQL — press Enter and watch it run for real:

```run
SELECT current_database();
```

  That name is this task's own private database.

---

TWO LANGUAGES AT ONE PROMPT

  At a psql prompt you type two very different kinds of thing:

    SQL statements      the database language. Sent to the SERVER.
                        End with a semicolon `;` — psql keeps reading
                        (even across lines) until it sees one.

    meta-commands       start with a backslash, like `\dt`. Handled by
                        the psql CLIENT itself — never sent to the server,
                        one per line, NO semicolon needed.

  The meta-commands are your eyes. The five you'll use constantly:

    \l          list all databases on the server
    \c <db>     connect to a different database
    \dt         list the tables in the current database
    \d <name>   describe one table: its columns, types, indexes
    \q          quit psql

---

  Try the eyes. First, every database on the server — you'll spot the
  `pgtrain_` prefix on task databases, plus Postgres's own built-ins
  (`postgres`, `template0`, `template1`):

```run
\l
```

  Now the tables inside THIS task's database:

```run
\dt
```

  Two tables. What's actually in the `books` one — column by column?

```run
\d books
```

  `\d` shows each column's name and type, and which column is the primary
  key. You haven't written a line of SQL and you already know the shape of
  the data — that's the habit: `\dt` then `\d` before you query anything.

---

SEEING THE DATA ITSELF

  Meta-commands show structure; to see the ROWS you need SQL. The one
  statement to know today (the next lesson makes a meal of it):

```run
SELECT * FROM books;
```

  `SELECT * FROM <table>;` means "give me every column of every row". Note
  the semicolon — that's what tells psql the statement is finished and can be
  sent to the server.

---

LIVING IN psql

  Three comforts that make the prompt feel like home — they only exist in a
  real interactive session, so pick `t` on the next block and try them
  yourself:

    Tab         completes table and column names: type `SELECT * FROM bo`
                and press Tab.
    Up-arrow    brings back your previous commands to edit and re-run.
    ;           if psql shows a continuation prompt (the dash in
                `pgtrain_...-#`), it's still waiting for your semicolon.

  And when you're done exploring, `\q` (or Ctrl-D) leaves psql. Outside a
  lesson you can open this same session any time with
  `pgtrain psql <task-id>`.

```run
SELECT title, year FROM books;
```

---

GOTCHAS

  - SQL needs the `;`. If nothing happens when you press Enter, psql is
    still waiting for it — look for the `-#` continuation prompt.
  - Meta-commands are NOT SQL: backslash, one line, no semicolon. `\dt;`
    works but the `;` does nothing; `SELECT * FROM books` without `;` sends
    nothing at all.
  - `\d books` describes the table; `SELECT * FROM books;` shows its rows.
    Structure vs data — you'll want both, in that order.
  - Every task has its OWN database. If a table "isn't there", check
    `SELECT current_database();` — you may be connected to the wrong one
    (`\c <db>` switches).

YOUR TURN

  The task: explore this database with `\dt` and `\d`, find the table that
  stores books, and write a query in `solution.sql` returning every row and
  every column of it.
