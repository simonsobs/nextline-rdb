from logging import getLogger
from pathlib import Path
from typing import Optional

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

import nextline_rdb

from . import models

ALEMBIC_INI = str(Path(nextline_rdb.__file__).resolve().parent / 'alembic.ini')


assert Path(ALEMBIC_INI).is_file()


def create_tables(engine: Engine) -> None:
    '''Define tables in the database based on the ORM models .

    https://docs.sqlalchemy.org/en/20/orm/quickstart.html#emit-create-table-ddl
    '''
    models.Model.metadata.create_all(bind=engine)


class DB:
    '''The interface to the SQLAlchemy database.

    An example usage:
    >>> with DB() as db:
    ...     # Nested session contexts
    ...     with db.session() as session:
    ...         with session.begin():
    ...             pass
    ...     # Direct begin
    ...     with db.session.begin() as session:
    ...         pass

    An alternative usage:
    >>> db = DB()
    >>> db.start()
    >>> with db.session() as session:
    ...     with session.begin():
    ...         pass
    >>> db.close()

    '''

    def __init__(
        self,
        url: Optional[str] = None,
        create_engine_kwargs: Optional[dict] = None,
    ):
        self.url = url or 'sqlite://'
        self.create_engine_kwargs = create_engine_kwargs or {}
        self.engine = create_engine(self.url, **self.create_engine_kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.url!r}>'

    def start(self) -> None:
        logger = getLogger(__name__)
        logger.info(f"SQLAlchemy DB URL: {self.url}")
        migrate_to_head(self.engine)
        create_tables(self.engine)  # NOTE: unnecessary as alembic is used
        with self.engine.connect() as connection:
            context = MigrationContext.configure(connection)
            rev = context.get_current_revision()
        logger.info(f"Alembic migration version: {rev!s}")
        self.session = sessionmaker(self.engine, expire_on_commit=False)

    def close(self) -> None:
        pass

    def __enter__(self) -> 'DB':
        self.start()
        return self

    def __exit__(self, *_, **__) -> None:
        self.close()


def migrate_to_head(engine: Engine) -> None:
    '''Run alembic to upgrade the database to the latest version.'''
    config = Config(ALEMBIC_INI)

    # config.set_main_option('sqlalchemy.url', str(engine.url))
    # from alembic import command
    # command.upgrade(config, "head")

    # NOTE: The commented out lines of command.upgrade() above would work fine
    # for a persistent DB. Here, the following code is instead used so that the
    # migration actually takes place for an in-memory DB as well for testing.

    script = ScriptDirectory.from_config(config)

    def upgrade(rev: str, context):  # type: ignore[no-untyped-def]
        del context
        return script._upgrade_revs('head', rev)

    context = EnvironmentContext(config, script, fn=upgrade)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=models.Model.metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
