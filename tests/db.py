from typing import Optional, Type

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from nextline_rdb import models
from nextline_rdb.utils import ensure_async_url, ensure_sync_url


class DB:
    '''The interface to the SQLAlchemy database.

    >>> db = DB()
    >>> with db.session() as session:
    ...     with session.begin():
    ...         pass

    >>> with db.session.begin() as session:
    ...     pass

    '''

    def __init__(
        self,
        url: Optional[str] = None,
        model_base_class: Type[DeclarativeBase] = models.Model,
        echo: bool = False,
    ):
        url = url or 'sqlite://'
        self.url = ensure_sync_url(url)
        self.model_base_class = model_base_class
        self.metadata = self.model_base_class.metadata
        self.engine = create_engine(self.url, echo=echo)
        self.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(self.engine, expire_on_commit=False)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.url!r}>'


class AsyncDB:
    '''The interface to the async SQLAlchemy database.

    >>> async def main():
    ...     # An example usage
    ...     async with AsyncDB() as db:
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
    ...     db = AsyncDB()
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
        model_base_class: Type[DeclarativeBase] = models.Model,
        echo: bool = False,
    ):
        url = url or 'sqlite+aiosqlite://'
        self.url = ensure_async_url(url)
        self.model_base_class = model_base_class
        self.metadata = self.model_base_class.metadata
        self.engine = create_async_engine(self.url, echo=echo)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.url!r}>'

    async def start(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def aclose(self) -> None:
        await self.engine.dispose()

    async def __aenter__(self) -> 'AsyncDB':
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore[no-untyped-def]
        del exc_type, exc_value, traceback
        await self.aclose()
