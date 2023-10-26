import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.models import Prompt
from nextline_rdb.tests.strategies.models import st_model_prompt

from .funcs import DB


@given(st.data())
async def test_repr(data: st.DataObject):
    async with DB() as Session:
        async with (Session() as session, session.begin()):
            model = data.draw(st_model_prompt())
            session.add(model)

        async with Session() as session:
            rows = await session.scalars(
                select(Prompt).options(
                    selectinload(Prompt.run), selectinload(Prompt.trace)
                )
            )
            for row in rows:
                repr_ = repr(row)
                assert Prompt, datetime  # type: ignore[truthy-function]
                assert repr_ == repr(eval(repr_))
