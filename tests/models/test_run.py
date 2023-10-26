import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Run
from nextline_rdb.tests.strategies.models import st_model_run

from .funcs import DB


@given(st.data())
async def test_repr(data: st.DataObject):
    async with DB() as Session:
        async with (Session() as session, session.begin()):
            model = data.draw(st_model_run())
            session.add(model)

        async with Session() as session:
            rows = await session.scalars(select(Run))
            for row in rows:
                repr_ = repr(row)
                assert Run, datetime
                assert repr_ == repr(eval(repr_))
