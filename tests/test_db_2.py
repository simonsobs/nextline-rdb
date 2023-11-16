from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import inspect

from nextline_rdb.db import DB
from nextline_rdb.models import Model
from nextline_rdb.models.strategies import st_model_run_list


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


@given(st.data())
def test_one(tmp_url_factory: Callable[[], str], data: st.DataObject):
    runs = data.draw(st_model_run_list(generate_traces=True, min_size=1, max_size=2))

    url = tmp_url_factory()

    db = DB(url)
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


@pytest.fixture(scope='session')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite:///{dir}/db.sqlite'
        return url

    return factory
