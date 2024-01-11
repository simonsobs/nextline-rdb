from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.utils import ensure_sync_url

from .models import Bar, Foo, Model


async def test_ensure_sync_url(tmp_url_factory: Callable[[], str]):
    url = tmp_url_factory()
    sync_url = ensure_sync_url(url)

    async with DB(url=sync_url) as db:
        assert db.url == url


async def test_fields():
    db = DB()
    assert db.url
    assert db.metadata
    assert db.engine

    async with db:
        assert db.session


@given(st.booleans())
async def test_migration_revision(use_migration: bool) -> None:
    async with DB(use_migration=use_migration) as db:
        if use_migration:
            assert db.migration_revision
        else:
            assert db.migration_revision is None


@given(st.lists(st.integers(min_value=0, max_value=4), min_size=0, max_size=4))
async def test_session(tmp_url_factory: Callable[[], str], sizes: list[int]):
    url = tmp_url_factory()

    objs = [Foo(bars=[Bar() for _ in range(size)]) for size in sizes]

    async with DB(url=url, model_base_class=Model, use_migration=False) as db:
        async with db.session() as session:
            async with session.begin():
                session.add_all(objs)
                saved = sorted(session.new, key=lambda x: (x.__class__.__name__, x.id))
                model_classes = {type(x) for x in saved}
        repr_saved = [repr(m) for m in saved]
        assert len(saved) == sum(sizes) + len(sizes)

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
