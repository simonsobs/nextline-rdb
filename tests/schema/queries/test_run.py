import strawberry
from hypothesis import given, note
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query
from nextline_rdb.utils.strategies import st_graphql_ints, st_none_or

from ..graphql import QUERY_RDB_RUN


@st.composite
def st_query_variables(
    draw: st.DrawFn, runs: list[Run]
) -> tuple[dict[str, int | None], Run | None]:
    run = draw(st_none_or(st.sampled_from(runs)) if runs else st.none())
    if run:
        id = draw(st.sampled_from([None, run.id]))
        run_no = run.run_no if id is None else None
        variables = {'id': id, 'runNo': run_no}
        return variables, run

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
    return variables, None


@given(st.data())
async def test_run(data: st.DataObject) -> None:
    schema = strawberry.Schema(query=Query)

    runs = data.draw(st_model_run_list(generate_traces=False, min_size=0, max_size=5))

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        note(f'runs: {runs}')

        variables, run = data.draw(st_query_variables(runs=runs))

        resp = await schema.execute(
            QUERY_RDB_RUN, variable_values=variables, context_value={'db': db}
        )
        note(f'resp: {resp}')

        assert resp.data

        run_ = resp.data['rdb']['run']

        if run is None:
            assert run_ is None
        else:
            assert run_
            assert run_['id'] == run.id
            assert run_['runNo'] == run.run_no
