import datetime

from hypothesis import given
from sqlalchemy import select

from nextline_rdb.db import DB

from .. import Model, TraceCall
from ..strategies import st_model_trace_call


@given(instance=st_model_trace_call())
async def test_repr(instance: TraceCall) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(instance)

        async with db.session() as session:
            stmt = select(TraceCall)
            row = (await session.execute(stmt)).scalar_one()

            repr_ = repr(row)
            assert datetime  # type: ignore[truthy-function]
            assert repr_ == repr(eval(repr_))
