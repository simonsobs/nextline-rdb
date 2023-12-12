from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.models import Model
from nextline_rdb.models.strategies import st_model_run_list
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


@given(st_model_run_list(generate_traces=True, max_size=3))
async def test_session_nested(tmp_url_factory: Callable[[], str], runs: list[Model]):
    url = tmp_url_factory()

    async with AsyncDB(url=url) as db:
        async with db.session() as session:
            async with session.begin():
                session.add_all(runs)
                saved = sorted(session.new, key=lambda x: (x.__class__.__name__, x.id))
                model_classes = {type(x) for x in saved}
        repr_saved = [repr(m) for m in saved]

        async with db.session() as session:
            loaded = sorted(
                [
                    m
                    for cls in model_classes
                    for m in (await session.scalars(select(cls))).all()
                ],
                key=lambda x: (x.__class__.__name__, x.id),
            )
            repr_loaded = [repr(m) for m in loaded]

        assert repr_saved == repr_loaded


@given(st_model_run_list(generate_traces=True, max_size=3))
async def test_session_begin(tmp_url_factory: Callable[[], str], runs: list[Model]):
    url = tmp_url_factory()

    async with AsyncDB(url=url) as db:
        async with db.session.begin() as session:
            session.add_all(runs)
            saved = sorted(session.new, key=lambda x: (x.__class__.__name__, x.id))
            model_classes = {type(x) for x in saved}
        repr_saved = [repr(m) for m in saved]

        async with db.session() as session:
            loaded = sorted(
                [
                    m
                    for cls in model_classes
                    for m in (await session.scalars(select(cls))).all()
                ],
                key=lambda x: (x.__class__.__name__, x.id),
            )
            repr_loaded = [repr(m) for m in loaded]

        assert repr_saved == repr_loaded


@pytest.fixture(scope='session')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite+aiosqlite:///{dir}/db.sqlite'
        return url

    return factory
