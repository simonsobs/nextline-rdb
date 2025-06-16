import pytest
import strawberry
from strawberry.types import ExecutionResult

from nextline_rdb.db import DB
from nextline_rdb.schema import Query
from tests.schema.graphql import QUERY_RDB_RUNS

from .utils import Cursor, Variables

params = [
    pytest.param(
        Variables(first=5, last=5),
        id='first-and-last',
    ),
    pytest.param(
        Variables(before=Cursor(31), first=5),
        id='before-and-first',
    ),
    pytest.param(
        Variables(after=Cursor(20), last=5),
        id='after-and-last',
    ),
    pytest.param(
        Variables(before=Cursor(31), after=Cursor(20)),
        id='before-and-after',
    ),
    pytest.param(
        Variables(before=Cursor(31), after=Cursor(20), first=5, last=5),
        id='all',
    ),
]


@pytest.mark.parametrize('variables', params)
async def test_mixed_forward_and_backward(variables: Variables) -> None:
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        resp = await schema.execute(
            QUERY_RDB_RUNS,
            variable_values=dict(variables),
            context_value={'db': db},
        )

        assert isinstance(resp, ExecutionResult)
        assert not resp.data
        assert resp.errors
