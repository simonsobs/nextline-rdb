import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run

from ..db import AsyncDB


@given(st.data())
async def test_repr(data: st.DataObject):
    async with AsyncDB() as db:
        async with db.session.begin() as session:
            model = data.draw(st_model_run())
            session.add(model)

        async with db.session() as session:
            rows = await session.scalars(select(Run))
            for row in rows:
                repr_ = repr(row)
                assert Run, datetime  # type: ignore[truthy-function]
                assert repr_ == repr(eval(repr_))
