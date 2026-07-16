# Your first queries: SELECT, *, and LIMIT

The `snacks` table holds one row per snack in a vending machine:

| column | type    |
|--------|---------|
| id     | integer |
| name   | text    |
| price  | numeric |
| stock  | integer |

Write a query in `solution.sql` that returns the **name** and **price** of
**every** snack — those two columns, in that order, and no others. No
filtering, no sorting: this task is purely about choosing columns.

Row order does not matter.

> Grading runs your query and the reference against the same seeded database
> and compares the result sets — any query that produces the right rows passes.
