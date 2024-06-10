from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB

from ... import Model, TraceCall
from .. import st_model_trace_call


@given(st.data())
async def test_st_model_trace_call(data: st.DataObject) -> None:
    trace_call = data.draw(st_model_trace_call())

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(trace_call)
        async with db.session() as session:
            select_trace_call = select(TraceCall)
            select_trace_call = select_trace_call.options(
                selectinload(TraceCall.run),
                selectinload(TraceCall.trace),
                selectinload(TraceCall.prompts),
            )
            trace_call_ = await session.scalar(select_trace_call)
            assert trace_call_
            session.expunge_all()
    assert repr(trace_call) == repr(trace_call_)
