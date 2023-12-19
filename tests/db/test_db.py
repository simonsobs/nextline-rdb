from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.utils import ensure_async_url

from .models import Bar, Foo, Model


def test_ensure_sync_url(tmp_url_factory: Callable[[], str]):
    url = tmp_url_factory()
    async_url = ensure_async_url(url)

    with DB(url=async_url) as db:
        assert db.url == url


def test_fields():
    db = DB()
    assert db.url
    assert db.metadata
    assert db.engine

    with db:
        assert db.session


@given(st.booleans())
def test_migration_revision(use_migration: bool) -> None:
    with DB(use_migration=use_migration) as db:
        if use_migration:
            assert db.migration_revision
        else:
            assert db.migration_revision is None


@given(st.lists(st.integers(min_value=0, max_value=4), min_size=0, max_size=4))
def test_session(tmp_url_factory: Callable[[], str], sizes: list[int]):
    url = tmp_url_factory()

    objs = [Foo(bars=[Bar() for _ in range(size)]) for size in sizes]

    with DB(url=url, model_base_class=Model, use_migration=False) as db:
        with db.session() as session:
            with session.begin():
                session.add_all(objs)
                saved = sorted(session.new, key=lambda x: (x.__class__.__name__, x.id))
                model_classes = {type(x) for x in saved}
        repr_saved = [repr(m) for m in saved]
        assert len(saved) == sum(sizes) + len(sizes)

        with db.session() as session:
            loaded = sorted(
                [m for cls in model_classes for m in session.query(cls)],
                key=lambda x: (x.__class__.__name__, x.id),
            )
            repr_loaded = [repr(m) for m in loaded]

        assert repr_saved == repr_loaded


@pytest.fixture(scope='session')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite:///{dir}/db.sqlite'
        return url

    return factory
