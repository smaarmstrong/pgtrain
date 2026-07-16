# Reading errors and query output

The `plants` table holds one row per houseplant:

| column    | type    | note              |
|-----------|---------|-------------------|
| id        | integer |                   |
| name      | text    |                   |
| room      | text    | can be NULL       |
| waterings | integer |                   |

Your workspace `solution.sql` starts with a query that is **supposed** to
return two columns for every plant — its `name`, and the fixed text label
`houseplant` as a second column — but it fails with an error.

Run it (`pgtrain check`, or paste it into `pgtrain psql <id>`), **read the
error message**, and fix the query. There are two classic mistakes in it;
the error text points straight at the first one.

> Grading runs your query and the reference against the same seeded database
> and compares the result sets — any query that produces the right rows passes.
