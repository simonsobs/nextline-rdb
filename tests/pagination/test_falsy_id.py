import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from nextline_rdb.pagination import SortField, load_models

from .models import Entity

params = [
    pytest.param(
        dict(sort=[SortField("num")]),
        [6, 7, 8, 9, 3, 4, 5, 0, 1, 2],
    ),
    pytest.param(
        dict(sort=[SortField("num")], after=0),
        [1, 2],
    ),
    pytest.param(
        dict(sort=[SortField("num")], before=0),
        [6, 7, 8, 9, 3, 4, 5],
    ),
]


@pytest.mark.parametrize("kwargs, expected", params)
async def test_one(session: AsyncSession, kwargs, expected):
    Model = Entity
    id_field = "id"
    models = await load_models(session, Model, id_field, **kwargs)
    assert expected == [m.id for m in models]


params = [
    pytest.param(
        dict(sort=[SortField("num")]),
        ["F", "G", "H", "I", "C", "D", "E", "", "A", "B"],
    ),
    pytest.param(
        dict(sort=[SortField("num")], after=""),
        ["A", "B"],
    ),
    pytest.param(
        dict(sort=[SortField("num")], before=""),
        ["F", "G", "H", "I", "C", "D", "E"],
    ),
]


@pytest.mark.parametrize("kwargs, expected", params)
async def test_str(session: AsyncSession, kwargs, expected):
    Model = Entity
    id_field = "txt"
    models = await load_models(session, Model, id_field, **kwargs)
    assert expected == [getattr(m, id_field) for m in models]


@pytest.fixture
async def sample(db: async_sessionmaker):
    async with db.begin() as session:
        num = [3, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        txt = ["", "A", "B", "C", "D", "E", "F", "G", "H", "I"]
        for i in range(10):
            model = Entity(id=i, num=num[i], txt=txt[i])
            session.add(model)
