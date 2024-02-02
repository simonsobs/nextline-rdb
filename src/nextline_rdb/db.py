from collections.abc import Callable
from logging import getLogger
from os import PathLike
from pathlib import Path
from typing import Optional, Type

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, Engine, MetaData, event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

import nextline_rdb
from nextline_rdb import models
from nextline_rdb.utils import ensure_async_url

_PACKAGE_TOP = Path(nextline_rdb.__file__).resolve().parent
ALEMBIC_INI = str(_PACKAGE_TOP / 'alembic' / 'alembic.ini')


assert Path(ALEMBIC_INI).is_file()


class DB:
    '''The interface to the async SQLAlchemy database.

    >>> async def main():
    ...     # An example usage
    ...     async with DB() as db:
    ...         # nested session contexts
    ...         async with db.session() as session:
    ...             async with session.begin():
    ...                 # commit automatically
    ...                 pass
    ...         # can begin directly
    ...         async with db.session.begin() as session:
    ...             # commit automatically
    ...             pass
    ...
    ...     # An alternative usage
    ...     db = DB()
    ...     await db.start()
    ...     async with contextlib.aclosing(db):
    ...         async with db.session() as session:
    ...             async with session.begin():
    ...                 pass
    ...
    >>> import asyncio
    >>> import contextlib
    >>> asyncio.run(main())

    '''

    def __init__(
        self,
        url: Optional[str] = None,
        create_async_engine_kwargs: Optional[dict] = None,  # e.g., {'echo': True}
        model_base_class: Type[DeclarativeBase] = models.Model,
        use_migration: bool = True,
        migration_revision_target: str = 'head',
        alembic_ini_path: str | PathLike = ALEMBIC_INI,
        register_session_events: Optional[
            Callable[[sessionmaker[Session]], None]
        ] = None,
    ):
        url = url or 'sqlite+aiosqlite://'
        self.url = ensure_async_url(url)
        self.create_async_engine_kwargs = create_async_engine_kwargs or {}
        self.model_base_class = model_base_class
        self.metadata = self.model_base_class.metadata
        self.use_migration = use_migration
        self.migration_revision_target = migration_revision_target
        self.alembic_ini_path = alembic_ini_path

        self.engine = create_async_engine(self.url, **self.create_async_engine_kwargs)
        self.migration_revision: str | None = None

        self._logger = getLogger(__name__)
        self._logger.info(f'Async SQLAlchemy DB URL: {self.url}')

        self._register_session_events = register_session_events

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.url!r}>'

    async def start(self) -> None:
        if self.use_migration:
            await self._migrate()
        else:
            await self._define_tables()

        self.migration_revision = await self._get_current_revision()
        self._logger.info(f'Alembic migration version: {self.migration_revision!s}')

        # As of SQLAlchemy 2.0, the async session maker cannot be use for
        # registering event hooks with the event.listen_for() function. Use the
        # sync session maker instead as described in the SQLAlchemy documentation:
        # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#examples-of-event-listeners-with-async-engines-sessions-sessionmakers

        sync_maker = sessionmaker()
        self.session = async_sessionmaker(
            self.engine, expire_on_commit=False, sync_session_class=sync_maker
        )

        if self._register_session_events:
            self._register_session_events(sync_maker)

    async def _migrate(self) -> None:
        assert Path(self.alembic_ini_path).is_file()
        config = Config(self.alembic_ini_path)
        await migrate(
            engine=self.engine,
            metadata=self.metadata,
            config=config,
            target=self.migration_revision_target,
        )

    async def _get_current_revision(self) -> str | None:
        def _fn(conn: Connection) -> str | None:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()

        async with self.engine.connect() as conn:
            return await conn.run_sync(_fn)

    async def _define_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)

    async def aclose(self) -> None:
        await self.engine.dispose()

    async def __aenter__(self) -> 'DB':
        await self.start()
        return self

    async def __aexit__(self, *_, **__) -> None:
        await self.aclose()


async def migrate(
    engine: AsyncEngine,
    metadata: MetaData,
    config: Config,
    target: str = 'head',
) -> None:
    script = ScriptDirectory.from_config(config)

    def upgrade(rev: str, context):  # type: ignore[no-untyped-def]
        del context
        return script._upgrade_revs(target, rev)

    context = EnvironmentContext(config, script, fn=upgrade)

    def do_run_migrations(connection: Connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    '''Enable foreign key constraints in SQLite.

    The code copied from the SQLAlchemy documentation:
    https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support
    '''
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
