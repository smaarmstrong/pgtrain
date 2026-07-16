# Meet the database: psql and the meta-commands

This task's database holds **two** tables. One of them stores books; the other
stores library members.

1. Open an interactive session on the task database:

       pgtrain psql foundations/01-meet-the-database

2. Look around: `\dt` lists the tables, `\d <name>` describes one, `\q` gets
   you back out.

3. In `solution.sql` (in your workspace), write the query that returns
   **every row and every column** of the table that stores the books.

> Grading runs your query and the reference against the same seeded database
> and compares the result sets — any query that produces the right rows passes.
