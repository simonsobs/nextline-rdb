import base64
import datetime
from typing import Any, Literal, Optional, TypedDict

import pytest
import strawberry

from nextline_rdb import AsyncDB
from nextline_rdb.models import Run
from nextline_rdb.schema import Query

from ..graphql import QUERY_HISTORY_RUNS


def Cursor(i: int) -> str:
    return base64.b64encode(f'{i}'.encode()).decode()


class Variables(TypedDict, total=False):
    before: str
    after: str
    first: int
    last: int


class PageInfo(TypedDict):
    hasPreviousPage: bool
    hasNextPage: bool
    startCursor: Optional[str]
    endCursor: Optional[str]


async def test_all(sample: None, db: AsyncDB) -> None:
    del sample
    variables = Variables()
    expected = (False, False, Cursor(1), Cursor(100))
    await assert_results(db, variables, expected)


params = [
    pytest.param(
        Variables(first=0),
        (False, True, None, None),
        id='zero',
    ),
    pytest.param(
        Variables(first=1),
        (False, True, Cursor(1), Cursor(1)),
        id='one',
    ),
    pytest.param(
        Variables(first=5),
        (False, True, Cursor(1), Cursor(5)),
        id='fewer-than-total',
    ),
    pytest.param(
        Variables(first=99),
        (False, True, Cursor(1), Cursor(99)),
        id='fewer-than-total-by-one',
    ),
    pytest.param(
        Variables(first=100),
        (False, False, Cursor(1), Cursor(100)),
        id='exactly-total',
    ),
    pytest.param(
        Variables(first=101),
        (False, False, Cursor(1), Cursor(100)),
        id='more-than-total-by-one',
    ),
    pytest.param(
        Variables(first=150),
        (False, False, Cursor(1), Cursor(100)),
        id='more-than-total',
    ),
]


@pytest.mark.parametrize('variables, expected', params)
async def test_forward(
    sample: None,
    db: AsyncDB,
    variables: Variables,
    expected: tuple[bool, bool, str | None, str | None],
):
    del sample
    await assert_results(db, variables, expected)


params = [
    pytest.param(
        Variables(after=Cursor(1)),
        (True, False, Cursor(2), Cursor(100)),
        id='one',
    ),
    pytest.param(
        Variables(after=Cursor(50)),
        (True, False, Cursor(51), Cursor(100)),
        id='middle',
    ),
    pytest.param(
        Variables(after=Cursor(99)),
        (True, False, Cursor(100), Cursor(100)),
        id='one-before-last',
    ),
    pytest.param(
        Variables(after=Cursor(100)),
        (True, False, None, None),
        id='last',
    ),
    pytest.param(
        Variables(after=Cursor(80), first=1),
        (True, True, Cursor(81), Cursor(81)),
        id='first-one',
    ),
    pytest.param(
        Variables(after=Cursor(80), first=19),
        (True, True, Cursor(81), Cursor(99)),
        id='first-fewer-than-count-by-one',
    ),
    pytest.param(
        Variables(after=Cursor(80), first=20),
        (True, False, Cursor(81), Cursor(100)),
        id='first-exactly-count',
    ),
    pytest.param(
        Variables(after=Cursor(80), first=21),
        (True, False, Cursor(81), Cursor(100)),
        id='first-more-than-count-by-one',
    ),
    pytest.param(
        Variables(after=Cursor(80), first=30),
        (True, False, Cursor(81), Cursor(100)),
        id='first-more-than-count',
    ),
    pytest.param(
        Variables(after=Cursor(100), first=0),
        (True, False, None, None),
        id='zero-after-last',
    ),
    pytest.param(
        Variables(after=Cursor(100), first=1),
        (True, False, None, None),
        id='one-after-last',
    ),
    pytest.param(
        Variables(after=Cursor(100), first=20),
        (True, False, None, None),
        id='some-after-last',
    ),
]


@pytest.mark.parametrize('variables, expected', params)
async def test_forward_with_after(
    sample: None,
    db: AsyncDB,
    variables: Variables,
    expected: tuple[bool, bool, str | None, str | None],
):
    del sample
    await assert_results(db, variables, expected)


params = [
    pytest.param(
        Variables(last=0),
        (True, False, None, None),
        id='zero',
    ),
    pytest.param(
        Variables(last=1),
        (True, False, Cursor(100), Cursor(100)),
        id='one',
    ),
    pytest.param(
        Variables(last=5),
        (True, False, Cursor(96), Cursor(100)),
        id='some',
    ),
    pytest.param(
        Variables(last=99),
        (True, False, Cursor(2), Cursor(100)),
        id='fewer-than-total-by-one',
    ),
    pytest.param(
        Variables(last=100),
        (False, False, Cursor(1), Cursor(100)),
        id='exactly-total',
    ),
    pytest.param(
        Variables(last=101),
        (False, False, Cursor(1), Cursor(100)),
        id='more-than-total-by-one',
    ),
    pytest.param(
        Variables(last=150),
        (False, False, Cursor(1), Cursor(100)),
        id='more-than-total',
    ),
]


@pytest.mark.parametrize('variables, expected', params)
async def test_backward(
    sample: None,
    db: AsyncDB,
    variables: Variables,
    expected: tuple[bool, bool, str | None, str | None],
):
    del sample
    await assert_results(db, variables, expected)


params = [
    pytest.param(
        Variables(before=Cursor(100)),
        (False, True, Cursor(1), Cursor(99)),
        id='end',
    ),
    pytest.param(
        Variables(before=Cursor(50)),
        (False, True, Cursor(1), Cursor(49)),
        id='middle',
    ),
    pytest.param(
        Variables(before=Cursor(2)),
        (False, True, Cursor(1), Cursor(1)),
        id='one-after-start',
    ),
    pytest.param(
        Variables(before=Cursor(1)),
        (False, True, None, None),
        id='start',
    ),
    pytest.param(
        Variables(before=Cursor(20), last=1),
        (True, True, Cursor(19), Cursor(19)),
        id='last-one',
    ),
    pytest.param(
        Variables(before=Cursor(20), last=18),
        (True, True, Cursor(2), Cursor(19)),
        id='last-fewer-than-count-by-one',
    ),
    pytest.param(
        Variables(before=Cursor(20), last=19),
        (False, True, Cursor(1), Cursor(19)),
        id='last-exactly-count',
    ),
    pytest.param(
        Variables(before=Cursor(20), last=20),
        (False, True, Cursor(1), Cursor(19)),
        id='last-more-than-count-by-one',
    ),
    pytest.param(
        Variables(before=Cursor(20), last=30),
        (False, True, Cursor(1), Cursor(19)),
        id='last-more-than-count',
    ),
]


@pytest.mark.parametrize('variables, expected', params)
async def test_backward_with_before(
    sample: None,
    db: AsyncDB,
    variables: Variables,
    expected: tuple[bool, bool, str | None, str | None],
):
    del sample
    await assert_results(db, variables, expected)


params = [
    pytest.param(
        Variables(),
        (False, False, Cursor(1), Cursor(1)),
        id='default',
    ),
    pytest.param(
        Variables(after=Cursor(1)),
        (True, False, None, None),
        id='forward-after-one',
    ),
    pytest.param(
        Variables(first=1),
        (False, False, Cursor(1), Cursor(1)),
        id='forward-first-one',
    ),
    pytest.param(
        Variables(after=Cursor(1), first=1),
        (True, False, None, None),
        id='forward-after-one-first-one',
    ),
    pytest.param(
        Variables(before=Cursor(1)),
        (False, True, None, None),
        id='backward-before-one',
    ),
    pytest.param(
        Variables(last=1),
        (False, False, Cursor(1), Cursor(1)),
        id='backward-last-one',
    ),
    pytest.param(
        Variables(before=Cursor(1), last=1),
        (False, True, None, None),
        id='backward-before-one-last-one',
    ),
]


@pytest.mark.parametrize('variables, expected', params)
async def test_one(
    sample_one: None,
    db: AsyncDB,
    variables: Variables,
    expected: tuple[bool, bool, str | None, str | None],
):
    del sample_one
    await assert_results(db, variables, expected)


@pytest.mark.parametrize('first_or_last', ['first', 'last'])
@pytest.mark.parametrize('number', [None, 0, 1, 5])
async def test_empty(
    sample_empty: None,
    db: AsyncDB,
    first_or_last: Literal['first', 'last'],
    number: int | None,
) -> None:
    del sample_empty
    variables = Variables()
    if number is not None:
        variables[first_or_last] = number
    expected = (False, False, None, None)
    await assert_results(db, variables, expected)


async def assert_results(
    db: AsyncDB,
    variables: Variables,
    expected: tuple[bool, bool, str | None, str | None],
) -> None:
    expected_page_info = PageInfo(
        hasPreviousPage=expected[0],
        hasNextPage=expected[1],
        startCursor=expected[2],
        endCursor=expected[3],
    )

    schema = strawberry.Schema(query=Query)
    resp = await schema.execute(
        QUERY_HISTORY_RUNS, variable_values=dict(variables), context_value={'db': db}
    )
    assert resp.data

    all_runs = resp.data['history']['runs']
    page_info = all_runs['pageInfo']
    edges = all_runs['edges']

    # print(page_info)
    # print(edges)

    assert expected_page_info == page_info

    if start_cursor := expected_page_info['startCursor']:
        edge = edges[0]
        assert start_cursor == edge['cursor']
        assert start_cursor == Cursor(edge['node']['id'])
    else:
        assert not edges

    if end_cursor := expected_page_info['endCursor']:
        edge = edges[-1]
        assert end_cursor == edge['cursor']
        assert end_cursor == Cursor(edge['node']['id'])
    else:
        assert not edges


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
async def test_error_forward_and_backward(
    sample: None, db: AsyncDB, variables: dict[str, Any]
) -> None:
    del sample

    schema = strawberry.Schema(query=Query)
    resp = await schema.execute(
        QUERY_HISTORY_RUNS, variable_values=variables, context_value={'db': db}
    )
    assert not resp.data
    assert resp.errors


@pytest.fixture
async def sample(db: AsyncDB) -> None:
    async with db.session.begin() as session:
        for run_no in range(11, 111):
            model = Run(
                run_no=run_no,
                state='running',
                started_at=datetime.datetime.utcnow(),
                ended_at=datetime.datetime.utcnow(),
                script='pass',
            )
            session.add(model)


@pytest.fixture
async def sample_one(db: AsyncDB) -> None:
    async with db.session.begin() as session:
        run_no = 10
        model = Run(
            run_no=run_no,
            state='running',
            started_at=datetime.datetime.utcnow(),
            ended_at=datetime.datetime.utcnow(),
            script='pass',
        )
        session.add(model)


@pytest.fixture
def sample_empty(db: AsyncDB) -> None:
    del db


@pytest.fixture
async def db() -> AsyncDB:
    async with AsyncDB() as db:
        yield db
