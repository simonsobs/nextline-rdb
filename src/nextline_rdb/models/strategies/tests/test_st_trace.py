from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.utils import safe_compare as sc
from nextline_rdb.utils.strategies import st_none_or
from nextline_rdb.utils.strategies.misc import st_graphql_ints

from ... import Model, Trace
from .. import st_model_run, st_model_trace, st_thread_task_no


@given(st.data())
async def test_st_model_trace(data: st.DataObject) -> None:
    run = data.draw(st_none_or(st_model_run(generate_traces=False)))
    trace_no = data.draw(st_none_or(st_graphql_ints(min_value=1)))
    thread_task_no = data.draw(st_none_or(st_thread_task_no()))
    generate_prompts = False if run else data.draw(st.booleans())

    trace = data.draw(
        st_model_trace(
            run=run,
            trace_no=trace_no,
            thread_task_no=thread_task_no,
            generate_prompts=generate_prompts,
        )
    )

    assert run is None or run is trace.run
    run = trace.run

    assert trace_no is None or trace_no == trace.trace_no
    assert thread_task_no is None or thread_task_no == (trace.thread_no, trace.task_no)

    assert sc(run.started_at) <= trace.started_at
    assert trace.started_at <= sc(trace.ended_at)
    assert sc(trace.ended_at) <= sc(run.ended_at)

    assert not generate_prompts or trace.prompts

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(trace)
        async with db.session() as session:
            stmt = select(Trace)
            trace_ = await session.scalar(stmt)
            session.expunge_all()
    assert repr(trace) == repr(trace_)
