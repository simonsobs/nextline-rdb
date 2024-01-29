import strawberry
from hypothesis import given, note
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Mutation, Query
from nextline_rdb.utils.strategies import st_graphql_ints

from ..graphql import MUTATE_RDB_DELETE_RUNS


@st.composite
def st_query_variables(
    draw: st.DrawFn, runs: list[Run]
) -> tuple[dict[str, list[int]], list[Run], list[Run]]:
    to_keep = list(runs)
    to_delete = list[Run]()
    ids = list[int]()
    while to_keep:
        run = draw(st.sampled_from(to_keep))
        to_keep.remove(run)
        to_delete.append(run)
        ids.append(run.id)
        if draw(st.booleans()):
            break
    extra = draw(
        st.lists(
            st_graphql_ints(min_value=1).filter(
                lambda i: i not in [run.id for run in runs]
            ),
            max_size=3,
            unique=True,
        )
    )
    ids.extend(extra)
    variables = {'ids': ids}
    return variables, to_keep, to_delete


@given(st.data())
async def test_delete_runs(data: st.DataObject) -> None:
    schema = strawberry.Schema(query=Query, mutation=Mutation)

    runs = data.draw(st_model_run_list(generate_traces=False, min_size=0, max_size=5))

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        variables, to_keep, to_delete = data.draw(st_query_variables(runs=runs))

        resp = await schema.execute(
            MUTATE_RDB_DELETE_RUNS,
            variable_values=variables,
            context_value={'db': db},
        )
        note(f'resp: {resp}')

        assert resp.data

        expected = {run.id for run in to_delete}
        assert set(resp.data['rdb']['deleteRuns']) == expected

        async with db.session() as session:
            stmt = select(Run)
            runs_ = (await session.scalars(stmt)).all()
            expected = {run.id for run in to_keep}
            assert {run.id for run in runs_} == expected
