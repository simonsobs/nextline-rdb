from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.models import Prompt
from nextline_rdb.models.strategies import (
    st_model_prompt,
    st_model_prompt_list,
    st_model_trace,
)
from nextline_rdb.utils.strategies import st_none_or

from ...db import AsyncDB


@given(st.data())
async def test_st_model_prompt(data: st.DataObject) -> None:
    prompt = data.draw(st_model_prompt())

    async with AsyncDB() as db:
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


@given(st.data())
async def test_st_model_prompt_lists(data: st.DataObject) -> None:
    trace = data.draw(st_none_or(st_model_trace(generate_prompts=False)))
    max_size = data.draw(st.integers(min_value=0, max_value=10))
    prompts = data.draw(st_model_prompt_list(trace=trace, max_size=max_size))

    assert len(prompts) <= max_size

    if prompts:
        traces = set(prompt.trace for prompt in prompts)
        assert len(traces) == 1
        assert trace is None or trace is traces.pop()

    async with AsyncDB() as db:
        async with db.session.begin() as session:
            session.add_all(prompts)

        async with db.session() as session:
            select_prompt = select(Prompt)
            prompts_ = (await session.scalars(select_prompt)).all()
            session.expunge_all()
    assert repr(prompts) == repr(prompts_)
