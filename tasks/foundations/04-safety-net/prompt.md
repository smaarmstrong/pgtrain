# You can't break anything: sandbox, reset, ROLLBACK

The `vault` table holds three irreplaceable items:

| id | item  |
|----|-------|
| 1  | deed  |
| 2  | will  |
| 3  | medal |

Work interactively:

    pgtrain psql foundations/04-safety-net

1. Inside a transaction, delete **everything** from `vault` — then change
   your mind and `ROLLBACK`. Check the three rows are still there.
2. Now make a change you mean: insert the row `(4, 'receipt')` and
   `COMMIT` it.

Grading asserts the **end state only**: the three original rows intact plus
your committed receipt row — exactly four rows. (It cannot tell whether you
did the rollback drill; do it anyway, that's the lesson.)

If you get the database into a mess at any point, that is the other half of
the lesson: `pgtrain reset foundations/04-safety-net` rebuilds it from seed.
