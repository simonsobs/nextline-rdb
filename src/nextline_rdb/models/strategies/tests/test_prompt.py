from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB

from ... import Model, Prompt
from .. import st_model_prompt


@given(st.data())
async def test_st_model_prompt(data: st.DataObject) -> None:
    prompt = data.draw(st_model_prompt())

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(prompt)
        async with db.session() as session:
            select_prompt = select(Prompt)
            prompt_ = await session.scalar(
                select_prompt.options(
                    selectinload(Prompt.run), selectinload(Prompt.trace)
                )
            )
            assert prompt_
            session.expunge_all()
    assert repr(prompt) == repr(prompt_)
