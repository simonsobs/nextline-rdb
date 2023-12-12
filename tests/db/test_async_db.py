from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.utils import ensure_sync_url


async def test_ensure_sync_url(tmp_url_factory: Callable[[], str]):
    url = tmp_url_factory()
    sync_url = ensure_sync_url(url)

    async with AsyncDB(url=sync_url) as db:
        assert db.url == url


async def test_fields():
    db = AsyncDB()
    assert db.url
    assert db.metadata
    assert db.engine

    async with db:
        assert db.session


@given(st.booleans())
async def test_migration_revision(use_migration: bool) -> None:
    async with AsyncDB(use_migration=use_migration) as db:
        if use_migration:
            assert db.migration_revision
        else:
            assert db.migration_revision is None


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


@pytest.fixture
def db():
    return AsyncDB()


@pytest.fixture(scope='session')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite+aiosqlite:///{dir}/db.sqlite'
        return url

    return factory
