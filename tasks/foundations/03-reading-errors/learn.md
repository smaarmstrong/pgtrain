THE IDEA

  An error message is not the database scolding you — it's the database
  HELPING you. Postgres errors are unusually good: they say what went wrong,
  point at where, and often suggest the fix. Learn to read them once and
  every future lesson gets easier, because you stop guessing.

  And remember where you are: a throwaway task database in a sealed
  container. An error changes NOTHING. The worst possible outcome of running
  broken SQL here is a red message — so let's go break things on purpose.

---

ANATOMY OF AN ERROR

  Here's a typo — `SELEC` instead of `SELECT`. Run it and look at the shape
  of what comes back:

```run
SELEC name FROM plants;
```

  Three parts, and they're always the same parts:

    ERROR:   what went wrong ("syntax error at or near ...")
    LINE 1:  your own statement echoed back
       ^     a caret pointing at the exact spot it gave up

  The caret is the gift. Don't read the whole statement — read the caret.

---

  Postgres goes further when it can guess what you meant. Misspell a COLUMN
  and you often get a HINT:

```run
SELECT nmae FROM plants;
```

  `ERROR: column "nmae" does not exist` — and a HINT suggesting
  `plants.name`. When a HINT appears, it's right more often than not.
  (You'll also meet DETAIL: — extra facts about the failure. One shows up
  at the end of this lesson.)

---

MISTAKE #1: THE MISSING SEMICOLON

  psql sends nothing until it sees `;` — it just keeps reading. So when you
  forget one and start typing the NEXT statement, both get glued together
  and the error lands strangely far from the real mistake:

```run
SELECT name FROM plants
SELECT id FROM plants;
```

  "syntax error at or near SELECT", pointing at line 2 — but the real sin
  is the missing `;` on line 1. When an error points at the START of a
  statement, look at the END of the one before it.

---

MISTAKE #2: WRONG QUOTES

  This one bites everyone exactly once. In SQL the two quote characters
  mean different things:

    'single quotes'   a text VALUE   — the data itself
    "double quotes"   an IDENTIFIER  — the NAME of a column or table

  So `"Fern"` doesn't mean the word Fern — it means "a column called Fern":

```run
SELECT "Fern" FROM plants;
```

  `column "Fern" does not exist` — of course it doesn't, it's a value, not
  a column. Say it with single quotes and it's just a piece of text,
  repeated for every row:

```run
SELECT 'Fern' FROM plants;
```

  Rule of thumb: data gets 'single', names get "double" (and you rarely
  need double at all — unquoted names work until a name has capitals or
  spaces in it).

---

THE WORST ERROR IS NO ERROR

  Case matters INSIDE text values. `'fern'` and `'Fern'` are different
  values, and comparing against the wrong one doesn't error — it just
  quietly matches nothing. (`WHERE` keeps only matching rows — the next
  lesson drills it properly.)

```run
SELECT name FROM plants WHERE name = 'fern';
```

  `(0 rows)` — no ERROR line, no caret, just an empty answer. An error
  stops you; a wrong answer follows you around. When a query returns
  nothing unexpectedly, suspect your values (case, spelling, spaces)
  before your syntax.

---

READING A RESULT SET

  Now the healthy output, and one thing worth a hard look — the `room`
  column:

```run
SELECT name, room FROM plants;
```

  Cactus's room shows as BLANK. That's NULL: not an empty string, but
  "no value recorded". By default psql prints NULL as nothing, which is
  easy to misread. You can make it visible (a client-side setting — note
  the backslash, it's a meta-command):

```run
\pset null '(null)'
SELECT name, room FROM plants;
```

  Same data, but now the absence has a face. The `(4 rows)` footer, the
  header line, and NULL's display are the three things to check before
  trusting any result.

---

  Promised earlier — a DETAIL line. Plant id 1 already exists, so inserting
  it again violates the primary key:

```run
INSERT INTO plants VALUES (1, 'Ivy', 'Hall', 3);
```

  `ERROR: duplicate key ...` says what rule broke; `DETAIL: Key (id)=(1)
  already exists` says exactly WHICH row collided. ERROR for what, DETAIL
  for specifics, HINT for the suggested fix — the full anatomy.

---

GOTCHAS

  - Read the caret (`^`) and the LINE number first, not the whole message.
  - An error pointing at the start of a statement often means a missing
    `;` at the end of the previous one.
  - 'single quotes' = text values. "double quotes" = column/table names.
    `= "Kitchen"` is asking for a COLUMN called Kitchen.
  - Text values are case-sensitive: `'fern'` is not `'Fern'` — and that
    mistake gives you 0 rows, not an error.
  - NULL prints as blank by default. `\pset null '(null)'` makes it
    visible for your session.
  - Errors here cost nothing. Run the broken thing, read, fix, re-run.

YOUR TURN

  The task: your workspace `solution.sql` holds a query with two of the
  classic mistakes above. Run it, read the error like you just practised,
  and fix it so it returns each plant's name plus the text label
  `houseplant`.
