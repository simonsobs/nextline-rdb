import strawberry
from hypothesis import Phase, given, note, settings
from hypothesis import strategies as st
from strawberry.types import ExecutionResult

from nextline_rdb.db import DB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query
from nextline_test_utils.strategies import st_graphql_ints, st_none_or
from tests.schema.graphql import QUERY_RDB_RUN


@st.composite
def st_query_variables_for_null_result(
    draw: st.DrawFn, runs: list[Run]
) -> dict[str, int | None]:
    id = draw(
        st_none_or(
            st_graphql_ints(min_value=1).filter(
                lambda i: i not in {run.id for run in runs}
            )
        )
    )
    run_no = (
        None
        if id is not None
        else draw(
            st_graphql_ints(min_value=1).filter(
                lambda i: i not in {run.run_no for run in runs}
            )
        )
    )
    variables = {'id': id, 'runNo': run_no}
    return variables


@st.composite
def st_query_variables(
    draw: st.DrawFn, run: Run | None, runs: list[Run]
) -> dict[str, int | None]:
    if run is None:
        return draw(st_query_variables_for_null_result(runs))

    id = draw(st.sampled_from([None, run.id]))
    run_no = run.run_no if id is None else None
    variables = {'id': id, 'runNo': run_no}
    return variables


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(st.data())
async def test_run(data: st.DataObject) -> None:
    schema = strawberry.Schema(query=Query)

    runs = data.draw(st_model_run_list(generate_traces=True, min_size=0, max_size=5))

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        run = data.draw(st_none_or(st.sampled_from(runs)) if runs else st.none())
        variables = data.draw(st_query_variables(run=run, runs=runs))

        resp = await schema.execute(
            QUERY_RDB_RUN, variable_values=variables, context_value={'db': db}
        )
        note(f'resp: {resp}')

        assert isinstance(resp, ExecutionResult)
        assert resp.data

        run_ = resp.data['rdb']['run']

        if run is None:
            assert run_ is None
        else:
            assert run_
            assert run_['id'] == run.id
            assert run_['runNo'] == run.run_no
