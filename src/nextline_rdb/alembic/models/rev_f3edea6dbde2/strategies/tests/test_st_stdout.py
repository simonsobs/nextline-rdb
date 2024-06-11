from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB

from ... import Model, Stdout
from .. import st_model_stdout


@given(st.data())
async def test_st_model_stdout(data: st.DataObject) -> None:
    stdout = data.draw(st_model_stdout())

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(stdout)
        async with db.session() as session:
            select_prompt = select(Stdout)
            stdout_ = await session.scalar(
                select_prompt.options(
                    selectinload(Stdout.run), selectinload(Stdout.trace)
                )
            )
            assert stdout_
            session.expunge_all()
    assert repr(stdout) == repr(stdout_)
