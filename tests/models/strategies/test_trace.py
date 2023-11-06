from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Trace
from nextline_rdb.models.strategies import st_model_trace
from nextline_rdb.utils import safe_compare as sc

from ...db import AsyncDB


@given(st.data())
async def test_st_model_run(data: st.DataObject) -> None:
    trace = data.draw(st_model_trace())

    run = trace.run
    assert sc(run.started_at) <= sc(trace.started_at)
    assert sc(trace.started_at) <= sc(trace.ended_at)
    assert sc(trace.ended_at) <= sc(run.ended_at)

    async with AsyncDB() as db:
        async with db.session.begin() as session:
            session.add(trace)
        async with db.session() as session:
            stmt = select(Trace)
            trace_ = await session.scalar(stmt)
            session.expunge_all()
    assert repr(trace) == repr(trace_)
