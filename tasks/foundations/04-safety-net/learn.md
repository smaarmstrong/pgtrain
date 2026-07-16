THE IDEA

  Fear is the real beginner's obstacle with databases — the sense that one
  wrong command destroys something that matters. So before the trainer asks
  you to create, alter and drop things freely, understand exactly why, HERE,
  that fear is pointless. You are standing inside three nested safety nets.

    net 1: the container   this whole Postgres lives in a Docker box,
                           `pgtrain-pg`. Your real machine, your real
                           projects, any real database you care about —
                           untouchable from in here. `pgtrain nuke` throws
                           the entire box away and a fresh one appears.

    net 2: the task DB     every task gets its OWN database, rebuilt from a
                           seed script. Wreck it and `pgtrain reset <task>`
                           gives you a pristine copy in about a second.

    net 3: transactions    Postgres itself has an undo: do your changes
                           inside a transaction and you can back out of ALL
                           of them, as if they never happened.

  Nets 1 and 2 belong to the trainer. Net 3 is the one you'll take with you
  to real databases — so that's the one we'll practise.

---

  Meet today's stakes. Three irreplaceable items:

```run
SELECT * FROM vault;
```

  Now watch me be reckless, safely.

---

THE TRANSACTION SAFETY NET

  A TRANSACTION is a group of changes Postgres treats as one all-or-nothing
  unit. Three words run it:

    BEGIN;      start the transaction — changes now stay PROVISIONAL
    ROLLBACK;   abandon everything since BEGIN, as if it never happened
    COMMIT;     the opposite: make everything since BEGIN permanent

  Here's the drill — delete EVERYTHING, look at the wreckage, then take it
  all back. This runs as one script; read the two counts:

```run
BEGIN;
DELETE FROM vault;
SELECT count(*) AS during_transaction FROM vault;
ROLLBACK;
SELECT count(*) AS after_rollback FROM vault;
```

  Inside the transaction the vault really was empty — the DELETE genuinely
  ran, this is no simulation. Then ROLLBACK, and three rows again. Nothing
  was ever at risk, because nothing was committed.

  That's the professional habit in miniature: about to run a scary UPDATE
  or DELETE on a database you care about? `BEGIN;` first, run it, LOOK at
  what changed — count the rows, SELECT a few — and only then choose
  `COMMIT;` or `ROLLBACK;`.

---

  COMMIT is the same ceremony with the opposite ending. Deposit a new item
  and make it stick:

```run
BEGIN;
INSERT INTO vault (id, item) VALUES (99, 'practice-run');
COMMIT;
SELECT * FROM vault;
```

  Four rows now — the insert survived, because we committed it. (One
  caution to file away: after COMMIT there is no rollback. The undo window
  is open between BEGIN and COMMIT, and only there.)

  Let's tidy our practice row away again — a DELETE we actually mean:

```run
DELETE FROM vault WHERE id = 99;
```

  Notice there was no BEGIN this time: a bare statement is its own tiny
  transaction that commits by itself the moment it succeeds. That's called
  AUTOCOMMIT, and it's why a bare DELETE on a real database is scary — the
  moment it runs, it's permanent. BEGIN is you switching the net on.

---

WHEN THE NET HAS ALREADY FAILED

  Suppose you didn't use a transaction, and the data is ruined. In this
  trainer that is a shrug: every task database is built by a seed script,
  and

      pgtrain reset <task-id>

  drops and rebuilds it, pristine. Your workspace files are backed up and
  restored too. There is no state you can get a task into that reset does
  not fix — which means the fastest way to learn here is to experiment
  hard, break things, and reset without guilt.

---

GOTCHAS

  - The undo window is BEGIN -> COMMIT/ROLLBACK. After COMMIT, it's
    permanent — rollback can't reach committed work.
  - Without BEGIN, every statement autocommits instantly. On practice data
    that's fine; on real data, BEGIN first and look before you COMMIT.
  - If psql tells you `current transaction is aborted` — an error happened
    mid-transaction — just `ROLLBACK;` and start the transaction again.
  - Left a transaction open and things seem stuck? `\q` quits psql, which
    rolls back anything uncommitted.
  - `pgtrain reset <task-id>` fixes ANY mess in a task database.

YOUR TURN

  The task, in `pgtrain psql`: run the rollback drill yourself — BEGIN,
  delete everything from `vault`, ROLLBACK, and check the three rows
  survived. Then insert `(4, 'receipt')` and COMMIT it. Grading checks the
  end state: the three originals plus your receipt.
