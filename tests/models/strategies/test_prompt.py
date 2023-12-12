from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.models import Prompt
from nextline_rdb.models.strategies import (
    st_model_prompt,
    st_model_prompt_list,
    st_model_run,
    st_model_trace_list,
)
from nextline_rdb.utils.strategies import st_none_or


@given(st.data())
async def test_st_model_prompt(data: st.DataObject) -> None:
    prompt = data.draw(st_model_prompt())

    async with AsyncDB(use_migration=False) as db:
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
    # generate_traces=False because that would generate a trace with prompts
    if run := data.draw(st_none_or(st_model_run(generate_traces=False))):
        data.draw(st_none_or(st_model_trace_list(run=run, min_size=0, max_size=5)))
        assert run.traces is not None

    max_size = data.draw(st.integers(min_value=0, max_value=10))

    prompts = data.draw(st_model_prompt_list(run=run, max_size=max_size))

    assert len(prompts) <= max_size

    if prompts:
        runs = set(prompt.trace.run for prompt in prompts)
        assert len(runs) == 1
        assert run is None or run is runs.pop()

    async with AsyncDB(use_migration=False) as db:
        async with db.session.begin() as session:
            session.add_all(prompts)

        async with db.session() as session:
            select_prompt = select(Prompt)
            prompts_ = (await session.scalars(select_prompt)).all()
            session.expunge_all()
    prompts = sorted(prompts, key=lambda prompt: prompt.id)
    assert repr(prompts) == repr(sorted(prompts_, key=lambda prompt: prompt.id))
