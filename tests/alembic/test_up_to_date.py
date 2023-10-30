from alembic import command
from alembic.config import Config


def test_migration_up_to_date(alembic_config_temp_sqlite: Config) -> None:
    '''Run alembic check

    This test fails if the head of the migration versions is not consistent of the ORM
    models defined in src/nextline_rdb/models.

    - https://github.com/sqlalchemy/alembic/releases/tag/rel_1_9_0
    - https://github.com/sqlalchemy/alembic/issues/724
    - https://github.com/sqlalchemy/alembic/pull/1101
    '''
    config = alembic_config_temp_sqlite
    command.upgrade(config, "head")  # This line might be unnecessary
    command.check(config)
