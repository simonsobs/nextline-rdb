import strawberry
from hypothesis import given, note, settings
from strawberry.types import ExecutionResult

from nextline_rdb.db import DB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query
from tests.schema.graphql import QUERY_RDB_RUNS

from .utils import Cursor, Edge, to_node


@settings(max_examples=20)
@given(runs=st_model_run_list(generate_traces=False, min_size=0, max_size=12))
async def test_property(runs: list[Run]) -> None:
    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        nodes_saved = [to_node(run) for run in runs]
        note(f'nodes_saved: {nodes_saved}')

        resp = await schema.execute(QUERY_RDB_RUNS, context_value={'db': db})
        assert isinstance(resp, ExecutionResult)
        assert resp.data

        all_runs = resp.data['rdb']['runs']
        edges: list[Edge] = all_runs['edges']

        nodes = [edge['node'] for edge in edges]
        cursors = [edge['cursor'] for edge in edges]

        assert cursors == [Cursor(node['id']) for node in nodes]
