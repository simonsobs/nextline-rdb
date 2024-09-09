import strawberry
from hypothesis import Phase, given, note, settings
from strawberry.types import ExecutionResult

from nextline_rdb.db import DB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query
from tests.schema.graphql import QUERY_RDB_CONNECTIONS


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(runs=st_model_run_list(generate_traces=True, min_size=0, max_size=3))
async def test_history(runs: list[Run]) -> None:
    note(f'runs: {runs}')

    schema = strawberry.Schema(query=Query)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)

        resp = await schema.execute(QUERY_RDB_CONNECTIONS, context_value={'db': db})

    assert isinstance(resp, ExecutionResult)
    assert resp.data
    rdb = resp.data['rdb']
    runs_ = rdb['runs']['edges']

    assert len(runs) == len(runs_)

    # TODO: Now only the number of runs is checked. Check the contents as well.
