from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.models import Trace
from nextline_rdb.models.strategies import (
    st_model_run,
    st_model_trace,
    st_model_trace_list,
    st_thread_task_no,
)
from nextline_rdb.utils import safe_compare as sc
from nextline_rdb.utils.strategies import st_none_or
from nextline_rdb.utils.strategies.misc import st_graphql_ints


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

    async with AsyncDB(use_migration=False) as db:
        async with db.session.begin() as session:
            session.add(trace)
        async with db.session() as session:
            stmt = select(Trace)
            trace_ = await session.scalar(stmt)
            session.expunge_all()
    assert repr(trace) == repr(trace_)


@given(st.data())
async def test_st_model_trace_lists(data: st.DataObject) -> None:
    run = data.draw(st_none_or(st_model_run(generate_traces=False)))
    max_size = data.draw(st.integers(min_value=0, max_value=10))
    traces = data.draw(st_model_trace_list(run=run, max_size=max_size))

    assert len(traces) <= max_size

    if traces:
        runs = set(trace.run for trace in traces)
        assert len(runs) == 1
        assert run is None or run is runs.pop()

    async with AsyncDB(use_migration=False) as db:
        async with db.session.begin() as session:
            session.add_all(traces)

        async with db.session() as session:
            stmt = select(Trace)
            traces_ = (await session.scalars(stmt)).all()
            session.expunge_all()

    assert repr(traces) == repr(traces_)
