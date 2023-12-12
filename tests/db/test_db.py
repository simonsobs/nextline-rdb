from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import inspect

from nextline_rdb.db import DB
from nextline_rdb.models import Model
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.utils import ensure_async_url


def object_state(obj: Model) -> str:
    insp = inspect(obj)
    if insp.transient:
        return 'transient'
    elif insp.pending:
        return 'pending'
    elif insp.persistent:
        return 'persistent'
    elif insp.deleted:
        return 'deleted'
    elif insp.detached:
        return 'detached'
    else:
        raise ValueError(f'Unknown state for {obj}')


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


@given(st_model_run_list(generate_traces=True, max_size=3))
def test_session_nested(tmp_url_factory: Callable[[], str], runs: list[Model]):
    url = tmp_url_factory()

    with DB(url) as db:
        with db.session() as session:
            with session.begin():
                session.add_all(runs)
                saved = sorted(session.new, key=lambda x: (x.__class__.__name__, x.id))
                model_classes = {type(x) for x in saved}
        repr_saved = [repr(m) for m in saved]

        with db.session() as session:
            loaded = sorted(
                (m for cls in model_classes for m in session.query(cls)),
                key=lambda x: (x.__class__.__name__, x.id),
            )
            repr_loaded = [repr(m) for m in loaded]

        assert repr_saved == repr_loaded


@given(st_model_run_list(generate_traces=True, max_size=3))
def test_session_begin(tmp_url_factory: Callable[[], str], runs: list[Model]):
    url = tmp_url_factory()

    with DB(url) as db:
        with db.session.begin() as session:
            session.add_all(runs)
            saved = sorted(session.new, key=lambda x: (x.__class__.__name__, x.id))
            model_classes = {type(x) for x in saved}
        repr_saved = [repr(m) for m in saved]

        with db.session() as session:
            loaded = sorted(
                (m for cls in model_classes for m in session.query(cls)),
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
