import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.alembic.models.rev_5a08750d6760 import Model, Prompt
from nextline_rdb.alembic.models.rev_5a08750d6760.strategies import st_model_prompt
from nextline_rdb.db.adb import AsyncDB


@given(st.data())
async def test_repr(data: st.DataObject):
    async with AsyncDB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            model = data.draw(st_model_prompt())
            session.add(model)

        async with db.session() as session:
            rows = await session.scalars(
                select(Prompt).options(
                    selectinload(Prompt.run), selectinload(Prompt.trace)
                )
            )
            for row in rows:
                repr_ = repr(row)
                assert Prompt, datetime  # type: ignore[truthy-function]
                assert repr_ == repr(eval(repr_))
