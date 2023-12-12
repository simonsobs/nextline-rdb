from typing import Optional, Type

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from nextline_rdb import models
from nextline_rdb.utils import ensure_async_url


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
        create_async_engine_kwargs: Optional[dict] = None,  # e.g., {'echo': True}
        model_base_class: Type[DeclarativeBase] = models.Model,
    ):
        url = url or 'sqlite+aiosqlite://'
        self.url = ensure_async_url(url)
        self.create_async_engine_kwargs = create_async_engine_kwargs or {}
        self.model_base_class = model_base_class
        self.metadata = self.model_base_class.metadata

        self.engine = create_async_engine(self.url, **self.create_async_engine_kwargs)

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
