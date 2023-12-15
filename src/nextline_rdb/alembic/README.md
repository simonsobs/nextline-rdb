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
