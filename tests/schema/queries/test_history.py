import strawberry
from hypothesis import given

from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query

from ..graphql import QUERY_HISTORY


@given(runs=st_model_run_list(generate_traces=True, min_size=0, max_size=3))
async def test_history(runs: list[Run]) -> None:
    schema = strawberry.Schema(query=Query)

    async with AsyncDB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)

        resp = await schema.execute(QUERY_HISTORY, context_value={'db': db})

    assert resp.data
    history = resp.data['history']
    runs_ = history['runs']['edges']

    assert len(runs) == len(runs_)

    # TODO: Now only the number of runs is checked. Check the contents as well.
