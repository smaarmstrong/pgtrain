# SQLAlchemy Core: aggregate against live Postgres

A real Postgres database (seeded for you) has a `sales` table:

| column | type    |
|--------|---------|
| id     | integer |
| region | text    |
| amount | numeric |

Edit `solution.py` and implement:

```python
def revenue_by_region(engine):
    ...
```

It receives a live SQLAlchemy `Engine` connected to the database and must
return a list of `(region, total_amount)` tuples — one per region, the total
being the **sum of `amount`** for that region — ordered by **total descending**,
then by **region ascending** to break ties.

Use **SQLAlchemy Core** (reflect the existing `sales` table with
`Table(..., autoload_with=engine)` and build a `select(...)`); don't hand-write
a raw SQL string.

Example (for the seeded data):

```python
[('east', 200), ('north', 135), ('south', 125)]
```

`total_amount` may be an `int`, `float`, or `Decimal` — the grader compares
numerically.

> The grader runs pytest in a venv (SQLAlchemy + psycopg) against the same
> Docker Postgres and checks the returned rows.
