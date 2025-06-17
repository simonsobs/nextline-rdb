import dataclasses
import datetime as dt
from typing import Optional

import strawberry
from hypothesis import Phase, given, note, settings
from hypothesis import strategies as st
from strawberry.types import ExecutionResult

from nextline_rdb.db import DB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query
from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_none_or
from tests.schema.graphql import QUERY_RDB_RUNS

from .utils import Edge, Filter, Node, PageInfo, Variables, dt_to_iso, to_node


@dataclasses.dataclass
class FilterSrc:
    started_after: dt.datetime | None
    started_before: dt.datetime | None
    ended_after: dt.datetime | None
    ended_before: dt.datetime | None

    def to_filter(self) -> Filter:
        return Filter(
            startedAfter=dt_to_iso(self.started_after),
            startedBefore=dt_to_iso(self.started_before),
            endedAfter=dt_to_iso(self.ended_after),
            endedBefore=dt_to_iso(self.ended_before),
        )


def st_filter_src() -> st.SearchStrategy[FilterSrc]:
    return st.builds(
        FilterSrc,
        started_after=st_none_or(st.datetimes()),
        started_before=st_none_or(st.datetimes()),
        ended_after=st_none_or(st.datetimes()),
        ended_before=st_none_or(st.datetimes()),
    )


@given(filter_src=st_filter_src())
def test_st_filter_src(filter_src: FilterSrc) -> None:
    filter_src.to_filter()


def is_selected(filter_src: FilterSrc | None, run: Run) -> bool:
    if filter_src is None:
        return True
    if not in_range(
        at=run.started_at,
        before=filter_src.started_before,
        after=filter_src.started_after,
    ):
        return False
    if not in_range(
        at=run.ended_at,
        before=filter_src.ended_before,
        after=filter_src.ended_after,
    ):
        return False
    return True


def in_range(
    at: dt.datetime | None, before: dt.datetime | None, after: dt.datetime | None
) -> bool:
    if at is None:
        if before is None and after is None:
            return True
        return False
    return sc(after) <= at < sc(before)


@settings(max_examples=20, phases=(Phase.generate,))  # Avoid shrinking
@given(
    runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12),
    filter_src=st_none_or(st_filter_src()),
)
async def test_all(runs: list[Run], filter_src: Optional[FilterSrc]) -> None:
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)

        nodes_selected = [to_node(run) for run in runs if is_selected(filter_src, run)]
        note(f'nodes_selected: {nodes_selected}')
        n_nodes_selected = len(nodes_selected)

        nodes_rejected = [
            to_node(run) for run in runs if not is_selected(filter_src, run)
        ]
        note(f'nodes_rejected: {nodes_rejected}')

        variables = Variables(filter=filter_src.to_filter() if filter_src else None)
        resp = await schema.execute(
            QUERY_RDB_RUNS,
            variable_values=dict(variables),
            context_value={'db': db},
        )
        assert isinstance(resp, ExecutionResult)
        assert resp.data

        all_runs = resp.data['rdb']['runs']
        page_info: PageInfo = all_runs['pageInfo']
        total_count = all_runs['totalCount']
        edges: list[Edge] = all_runs['edges']

        if edges:
            assert page_info['startCursor'] == edges[0]['cursor']
            assert page_info['endCursor'] == edges[-1]['cursor']

        assert total_count == n_nodes_selected

        nodes = [edge['node'] for edge in edges]

        assert nodes == list(reversed(nodes_selected))


@settings(max_examples=20, phases=(Phase.generate,))  # Avoid shrinking
@given(
    runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12),
    first=st.integers(min_value=1, max_value=15),
    filter_src=st_none_or(st_filter_src()),
)
async def test_forward(
    runs: list[Run], first: int, filter_src: Optional[FilterSrc]
) -> None:
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        nodes_selected = [to_node(run) for run in runs if is_selected(filter_src, run)]
        n_nodes_selected = len(nodes_selected)
        note(f'nodes_saved: {nodes_selected}')

        after = None
        has_next_page = True
        nodes = list[Node]()
        filter = filter_src.to_filter() if filter_src else None
        while has_next_page:
            variables = Variables(after=after, first=first, filter=filter)

            resp = await schema.execute(
                QUERY_RDB_RUNS,
                variable_values=dict(variables),
                context_value={'db': db},
            )
            assert isinstance(resp, ExecutionResult)
            assert resp.data

            all_runs = resp.data['rdb']['runs']
            page_info: PageInfo = all_runs['pageInfo']
            total_count = all_runs['totalCount']
            edges: list[Edge] = all_runs['edges']

            has_next_page = page_info['hasNextPage']
            after = page_info['endCursor']

            if not nodes_selected:
                assert not edges
                assert not has_next_page
                assert after is None

            if edges:
                assert after == edges[-1]['cursor']

            assert total_count == n_nodes_selected

            nodes.extend(edge['node'] for edge in edges)

        assert nodes == list(reversed(nodes_selected))


@settings(max_examples=20, phases=(Phase.generate,))  # Avoid shrinking
@given(
    runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12),
    last=st.integers(min_value=1, max_value=15),
    filter_src=st_none_or(st_filter_src()),
)
async def test_backward(
    runs: list[Run], last: int, filter_src: Optional[FilterSrc]
) -> None:
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        nodes_selected = [to_node(run) for run in runs if is_selected(filter_src, run)]
        n_nodes_selected = len(nodes_selected)
        note(f'nodes_saved: {nodes_selected}')

        before = None
        has_previous_page = True
        nodes = list[Node]()
        filter = filter_src.to_filter() if filter_src else None
        while has_previous_page:
            variables = Variables(before=before, last=last, filter=filter)

            resp = await schema.execute(
                QUERY_RDB_RUNS,
                variable_values=dict(variables),
                context_value={'db': db},
            )
            assert isinstance(resp, ExecutionResult)
            assert resp.data

            all_runs = resp.data['rdb']['runs']
            page_info: PageInfo = all_runs['pageInfo']
            total_count = all_runs['totalCount']
            edges: list[Edge] = all_runs['edges']

            has_previous_page = page_info['hasPreviousPage']
            before = page_info['startCursor']

            if not nodes_selected:
                assert not edges
                assert not has_previous_page
                assert before is None

            if edges:
                assert before == edges[0]['cursor']

            assert total_count == n_nodes_selected

            nodes.extend(edge['node'] for edge in reversed(edges))

        assert nodes == nodes_selected
