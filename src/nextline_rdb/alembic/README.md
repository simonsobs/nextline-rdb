# Alembic Migration Environment

This folder is the [Alembic Migration Environment](https://alembic.sqlalchemy.org/en/latest/tutorial.html#the-migration-environment).

## How to create a migration revision

In this folder, in which `alembic.ini` is located:

```bash
# Ensure the target DB doesn't exist
rm -f migration.sqlite3

# Create an empty up-to-date target DB
alembic upgrade head

# Generate a migration script
alembic revision --autogenerate -m 'message'

# Edit the generated migration script in `versions/` if necessary

# Apply the migration script to the target DB
alembic upgrade head

# Clean up
rm -f migration.sqlite3
```

### Copy ORM models (optonal)

Make a copy of the ORM models as needed. The ORM models can be used for data
migration and testing.

Copy the folder `src/nextline_rdb/models/` to `alembic/models/rev_{revision}/`.
The folder includes the ORM models, tests of the models, Hypothesis strategies
for the models, and the test of the strategies.

- An example data migration:
  [2024-06-10_10:15-5a61f247dd07.py](https://github.com/simonsobs/nextline-rdb/blob/v0.6.11/src/nextline_rdb/alembic/versions/2024-06-10_10%3A15-5a61f247dd07.py)
- An example migration test:
  [test_2024-06-10_12:02-15003e123b98.py](https://github.com/simonsobs/nextline-rdb/blob/v0.6.11/tests/alembic/migrations/test_2024-06-10_12%3A02-15003e123b98.py)

## Migration versions

| Revision ID  | ORM | Test | Date       | Type   | Note                      |
| ------------ | --- | ---- | ---------- | ------ | ------------------------- |
| 15003e123b98 |     | ✓    | 2024-06-10 | Schema | Remove columns            |
| f433a0a15c7e |     |      | 2024-06-10 | Schema | Update a constraint       |
| 5a61f247dd07 |     |      | 2024-06-10 | Data   |                           |
| f3edea6dbde2 | ✓   | ✓    | 2024-06-10 | Schema | Add a table               |
| 2cf3fc3d3dc5 |     | ✓    | 2024-06-10 | Schema | Remove columns            |
| ab0fe7b96033 |     |      | 2024-06-10 | Schema | Remove columns            |
| 269c15476fb1 |     |      | 2024-06-07 | Schema | Remove a column           |
| 8d24d9c2e9ba |     | ✓    | 2024-06-07 | Schema | Update constraints        |
| 4dc6a93dfed8 | ✓   | ✓    | 2024-02-04 | Schema | Remove a column           |
| 68cb1c590d1f |     |      | 2024-02-03 | Data   |                           |
| 245c4152e8d7 | ✓   |      | 2024-02-02 | Schema | Add a table               |
| c72fa3ee6a1a |     | ✓    | 2024-02-02 | Data   |                           |
| f9a742bb2297 | ✓   | ✓    | 2024-01-30 | Schema | Delete a column           |
| cafceacada62 |     |      | 2024-01-29 | Data   |                           |
| 6e3cf7d9b6bf | ✓   |      | 2024-01-29 | Schema | Add a table               |
| 2fa41efc56f0 |     |      | 2024-01-29 | Schema | Add a column              |
| 5a08750d6760 | ✓   |      | 2022-03-16 | Schema | Add columns, a constraint |
| de90b787e92f |     |      | 2022-03-14 | Schema | Add tables                |
