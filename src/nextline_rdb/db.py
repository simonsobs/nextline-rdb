from logging import getLogger
from pathlib import Path
from typing import Optional, Type

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import nextline_rdb
from nextline_rdb.utils import ensure_sync_url

from . import models

ALEMBIC_INI = str(Path(nextline_rdb.__file__).resolve().parent / 'alembic.ini')


assert Path(ALEMBIC_INI).is_file()


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
        create_engine_kwargs: Optional[dict] = None,  # e.g., {'echo': True}
        model_base_class: Type[DeclarativeBase] = models.Model,
        use_migration: bool = True,
    ):
        url = url or 'sqlite://'
        self.url = ensure_sync_url(url)
        self.create_engine_kwargs = create_engine_kwargs or {}
        self.model_base_class = model_base_class
        self.use_migration = use_migration

        self.engine = create_engine(self.url, **self.create_engine_kwargs)
        self.migration_revision: str | None = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.url!r}>'

    def start(self) -> None:
        logger = getLogger(__name__)
        logger.info(f'SQLAlchemy DB URL: {self.url}')

        if self.use_migration:
            self._migrate()
        else:
            self._define_tables()

        with self.engine.connect() as connection:
            context = MigrationContext.configure(connection)
            self.migration_revision = context.get_current_revision()
        logger.info(f'Alembic migration version: {self.migration_revision!s}')

        self.session = sessionmaker(self.engine, expire_on_commit=False)

    def _migrate(self) -> None:
        migrate_to_head(self.engine, model_base_class=self.model_base_class)

    def _define_tables(self) -> None:
        # https://docs.sqlalchemy.org/en/20/orm/quickstart.html#emit-create-table-ddl
        self.model_base_class.metadata.create_all(bind=self.engine)

    def close(self) -> None:
        pass

    def __enter__(self) -> 'DB':
        self.start()
        return self

    def __exit__(self, *_, **__) -> None:
        self.close()


def migrate_to_head(engine: Engine, model_base_class: Type[DeclarativeBase]) -> None:
    '''Run alembic to upgrade the database to the latest version.'''
    config = Config(ALEMBIC_INI)

    # config.set_main_option('sqlalchemy.url', str(engine.url))
    # from alembic import command
    # command.upgrade(config, 'head')

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
            target_metadata=model_base_class.metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
