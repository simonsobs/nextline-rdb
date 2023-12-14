from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base, Entity


@pytest.fixture
async def session(db: async_sessionmaker, sample) -> AsyncIterator[AsyncSession]:
    del sample
    async with db() as y:
        yield y


@pytest.fixture
async def sample(db: async_sessionmaker):
    async with db.begin() as session:
        num = [3, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        txt = ["AA", "BB", "AA", "AA", "BB", "AA", "AA", "BB", "AA", "BB"]
        for i in range(10):
            model = Entity(num=num[i], txt=txt[i])
            session.add(model)


@pytest.fixture
async def db(engine) -> async_sessionmaker:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    y = async_sessionmaker(bind=engine, expire_on_commit=False)
    return y


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    url = 'sqlite+aiosqlite://'
    y = create_async_engine(url)
    try:
        yield y
    finally:
        await y.dispose()
