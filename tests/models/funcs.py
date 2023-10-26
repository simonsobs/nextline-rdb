from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from nextline_rdb import models


@asynccontextmanager
async def DB() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await engine.dispose()
