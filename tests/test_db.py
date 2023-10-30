import pytest

from .db import DB


@pytest.fixture
def db():
    return DB()


def test_fields(db: DB):
    assert db.url
    assert db.models
    assert db.metadata
    assert db.engine
    assert db.session


def test_session(db: DB):
    with db.session() as session:
        with session.begin():
            pass


def test_session_maker(db: DB):
    with db.session.begin() as session:
        assert session
        pass
