import contextlib

import pytest

from .adb import AsyncDB


@pytest.fixture
def db():
    return AsyncDB()


async def test_fields(db: AsyncDB):
    assert db.url
    assert db.metadata
    assert db.engine
    await db.start()
    async with contextlib.aclosing(db):
        assert db.session


async def test_session(db: AsyncDB):
    async with db:
        async with db.session() as session:
            async with session.begin():
                pass


async def test_session_maker(db: AsyncDB):
    async with db:
        async with db.session.begin() as session:
            assert session
            pass
