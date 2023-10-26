import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.models import Stdout
from nextline_rdb.tests.strategies.models import st_model_stdout

from .funcs import DB


@given(st.data())
async def test_repr(data: st.DataObject):
    async with DB() as Session:
        async with (Session() as session, session.begin()):
            model = data.draw(st_model_stdout())
            session.add(model)

        async with Session() as session:
            rows = await session.scalars(
                select(Stdout).options(
                    selectinload(Stdout.run), selectinload(Stdout.trace)
                )
            )
            for row in rows:
                repr_ = repr(row)
                assert Stdout, datetime  # type: ignore[truthy-function]
                assert repr_ == repr(eval(repr_))
