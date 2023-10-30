import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.models import Trace
from nextline_rdb.tests.strategies.models import st_model_trace

from ..db import AsyncDB


@given(st.data())
async def test_repr(data: st.DataObject):
    async with AsyncDB() as db:
        async with db.session.begin() as session:
            model = data.draw(st_model_trace())
            session.add(model)

        async with db.session() as session:
            rows = await session.scalars(select(Trace).options(selectinload(Trace.run)))
            for row in rows:
                repr_ = repr(row)
                assert Trace, datetime  # type: ignore[truthy-function]
                assert repr_ == repr(eval(repr_))
