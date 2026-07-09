# Filter rows with WHERE

The `employees` table holds one row per employee:

| column     | type    |
|------------|---------|
| id         | integer |
| name       | text    |
| department | text    |
| salary     | numeric |

Write a query in `solution.sql` that returns the **name** and **salary** of
every employee who works in the **Engineering** department **and** earns
**more than 60000** (strictly greater — exactly 60000 does not count).

Return the two columns in that order. Row order does not matter.

> Grading runs your query and the reference against the same seeded database
> and compares the result sets — any query that produces the right rows passes.
