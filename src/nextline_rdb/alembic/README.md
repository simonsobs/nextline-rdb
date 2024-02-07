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

## ORM models for migration versions

Copy `src/nextline_rdb/models/` to `alembic/models/rev_{revision}/`.

The `models` folder includes the ORM models, tests of the models,
Hypothesis strategies for the models, and the test of the strategies.

The ORM models can be used for data migration and test migrations.

## Data migration

An example:
[2024-02-03_14:13-68cb1c590d1f.py](https://github.com/simonsobs/nextline-rdb/blob/v0.5.0/src/nextline_rdb/alembic/versions/2024-02-03_14%3A13-68cb1c590d1f.py)

## Test migrations

An example:
[test_2024-02-04_09:01-4dc6a93dfed8.py](https://github.com/simonsobs/nextline-rdb/blob/v0.5.0/tests/alembic/migrations/test_2024-02-04_09%3A01-4dc6a93dfed8.py)
