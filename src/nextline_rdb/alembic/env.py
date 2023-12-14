import asyncio
import logging
import logging.config

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from nextline_rdb import models

config = context.config
url = config.get_main_option("sqlalchemy.url")

if config.config_file_name:
    # from logging_tree import printout
    # printout()
    if config.cmd_opts is None:
        # Presumably, alembic.command.upgrade() or other functions from
        # alembic.command are called rather than the alembic command is
        # executed from a shell. Do not configure logging here so as to avoid
        # overriding the logging config.
        pass
    else:
        logging.config.fileConfig(config.config_file_name)


logger = logging.getLogger(__name__)
logger.info(f'DB URL: {url}')


target_metadata = models.Model.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    assert url is not None
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
