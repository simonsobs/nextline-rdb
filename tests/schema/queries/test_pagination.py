import base64
from typing import TypedDict

import pytest
import strawberry
from hypothesis import given, note
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query

from ..graphql import QUERY_RDB_RUNS


def Cursor(i: int) -> str:
    return base64.b64encode(f'{i}'.encode()).decode()


class Variables(TypedDict, total=False):
    before: str | None
    after: str | None
    first: int | None
    last: int | None


class PageInfo(TypedDict):
    hasPreviousPage: bool
    hasNextPage: bool
    startCursor: str | None
    endCursor: str | None


class Node(TypedDict):
    id: int
    runNo: int


class Edge(TypedDict):
    cursor: str
    node: Node


@given(runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12))
async def test_all(runs: list[Run]):
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        nodes_saved = [Node(id=run.id, runNo=run.run_no) for run in runs]
        n_nodes_saved = len(nodes_saved)
        note(f'nodes_saved: {nodes_saved}')

        resp = await schema.execute(QUERY_RDB_RUNS, context_value={'db': db})
        assert resp.data

        all_runs = resp.data['rdb']['runs']
        page_info: PageInfo = all_runs['pageInfo']
        total_count = all_runs['totalCount']
        edges: list[Edge] = all_runs['edges']

        if edges:
            assert page_info['startCursor'] == edges[0]['cursor']
            assert page_info['endCursor'] == edges[-1]['cursor']

        assert total_count == n_nodes_saved

        nodes = [edge['node'] for edge in edges]

        assert nodes == list(reversed(nodes_saved))


@given(
    runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12),
    first=st.integers(min_value=1, max_value=15),
)
async def test_forward(runs: list[Run], first: int):
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        nodes_saved = [Node(id=run.id, runNo=run.run_no) for run in runs]
        n_nodes_saved = len(nodes_saved)
        note(f'nodes_saved: {nodes_saved}')

        after = None
        has_next_page = True
        nodes = list[Node]()
        while has_next_page:
            variables = Variables(after=after, first=first)

            resp = await schema.execute(
                QUERY_RDB_RUNS,
                variable_values=dict(variables),
                context_value={'db': db},
            )
            assert resp.data

            all_runs = resp.data['rdb']['runs']
            page_info: PageInfo = all_runs['pageInfo']
            total_count = all_runs['totalCount']
            edges: list[Edge] = all_runs['edges']

            has_next_page = page_info['hasNextPage']
            after = page_info['endCursor']

            if not nodes_saved:
                assert not edges
                assert not has_next_page
                assert after is None

            if edges:
                assert after == edges[-1]['cursor']

            assert total_count == n_nodes_saved

            nodes.extend(edge['node'] for edge in edges)

        assert nodes == list(reversed(nodes_saved))


@given(
    runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12),
    last=st.integers(min_value=1, max_value=15),
)
async def test_backward(runs: list[Run], last: int):
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        nodes_saved = [Node(id=run.id, runNo=run.run_no) for run in runs]
        n_nodes_saved = len(nodes_saved)
        note(f'nodes_saved: {nodes_saved}')

        before = None
        has_previous_page = True
        nodes = list[Node]()
        while has_previous_page:
            variables = Variables(before=before, last=last)

            resp = await schema.execute(
                QUERY_RDB_RUNS,
                variable_values=dict(variables),
                context_value={'db': db},
            )
            assert resp.data

            all_runs = resp.data['rdb']['runs']
            page_info: PageInfo = all_runs['pageInfo']
            total_count = all_runs['totalCount']
            edges: list[Edge] = all_runs['edges']

            has_previous_page = page_info['hasPreviousPage']
            before = page_info['startCursor']

            if not nodes_saved:
                assert not edges
                assert not has_previous_page
                assert before is None

            if edges:
                assert before == edges[0]['cursor']

            assert total_count == n_nodes_saved

            nodes.extend(edge['node'] for edge in reversed(edges))

        assert nodes == nodes_saved


@given(runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12))
async def test_cursor(runs: list[Run]):
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        nodes_saved = [Node(id=run.id, runNo=run.run_no) for run in runs]
        note(f'nodes_saved: {nodes_saved}')

        resp = await schema.execute(QUERY_RDB_RUNS, context_value={'db': db})
        assert resp.data

        all_runs = resp.data['rdb']['runs']
        edges: list[Edge] = all_runs['edges']

        nodes = [edge['node'] for edge in edges]
        cursors = [edge['cursor'] for edge in edges]

        assert cursors == [Cursor(node['id']) for node in nodes]


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
async def test_error(variables: Variables) -> None:
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        resp = await schema.execute(
            QUERY_RDB_RUNS,
            variable_values=dict(variables),
            context_value={'db': db},
        )

        assert not resp.data
        assert resp.errors
