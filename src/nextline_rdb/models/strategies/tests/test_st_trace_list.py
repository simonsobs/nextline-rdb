from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.utils.strategies import st_none_or

from ... import Model, Trace
from .. import st_model_run, st_model_trace_list


@given(st.data())
async def test_st_model_trace_lists(data: st.DataObject) -> None:
    run = data.draw(st_none_or(st_model_run(generate_traces=False)))
    max_size = data.draw(st.integers(min_value=0, max_value=3))
    traces = data.draw(st_model_trace_list(run=run, max_size=max_size))

    assert len(traces) <= max_size

    if traces:
        runs = set(trace.run for trace in traces)
        assert len(runs) == 1
        assert run is None or run is runs.pop()

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(traces)

        async with db.session() as session:
            stmt = select(Trace)
            traces_ = (await session.scalars(stmt)).all()
            session.expunge_all()

    assert repr(traces) == repr(traces_)
