from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.utils.strategies import st_none_or

from ... import Model, Prompt
from .. import st_model_prompt_list, st_model_run, st_model_trace_list


@given(st.data())
async def test_st_model_prompt_lists(data: st.DataObject) -> None:
    # generate_traces=False because that would generate a trace with prompts
    if run := data.draw(st_none_or(st_model_run(generate_traces=False))):
        data.draw(st_none_or(st_model_trace_list(run=run, min_size=0, max_size=3)))
        assert run.traces is not None

    max_size = data.draw(st.integers(min_value=0, max_value=5))

    prompts = data.draw(st_model_prompt_list(run=run, max_size=max_size))

    assert len(prompts) <= max_size

    if prompts:
        runs = set(prompt.trace.run for prompt in prompts)
        assert len(runs) == 1
        assert run is None or run is runs.pop()

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(prompts)

        async with db.session() as session:
            select_prompt = select(Prompt)
            prompts_ = (await session.scalars(select_prompt)).all()
            session.expunge_all()
    prompts = sorted(prompts, key=lambda prompt: prompt.id)
    assert repr(prompts) == repr(sorted(prompts_, key=lambda prompt: prompt.id))
