from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.utils.strategies import st_ranges

from ... import Model, Prompt, Run, Stdout, Trace
from .. import st_model_run_list


@given(st.data())
async def test_options(data: st.DataObject) -> None:
    generate_traces = data.draw(st.booleans())
    min_size, max_size = data.draw(
        st_ranges(
            st_=st.integers,
            min_start=0,
            max_end=4,
            allow_start_none=False,
            allow_end_none=False,
        )
    )
    assert isinstance(min_size, int)
    assert isinstance(max_size, int)
    runs = data.draw(
        st_model_run_list(
            generate_traces=generate_traces, min_size=min_size, max_size=max_size
        )
    )
    assert min_size <= len(runs) <= max_size
    run_nos = [run.run_no for run in runs]
    assert run_nos == sorted(run_nos)

    traces = [trace for run in runs for trace in run.traces]
    prompts = [prompt for run in runs for prompt in run.prompts]
    stdouts = [stdout for run in runs for stdout in run.stdouts]

    if generate_traces is False:
        assert not traces
        assert not prompts
        assert not stdouts

    started_ats = [run.started_at for run in runs if run.started_at]
    assert started_ats == sorted(started_ats)


@given(runs=st_model_run_list(generate_traces=True, min_size=0, max_size=3))
async def test_db(runs: list[Run]) -> None:
    traces = [trace for run in runs for trace in run.traces]
    prompts = [prompt for run in runs for prompt in run.prompts]
    stdouts = [stdout for run in runs for stdout in run.stdouts]

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(runs)

        async with db.session() as session:
            select_run = select(Run)
            runs_ = (await session.scalars(select_run)).all()
            select_trace = select(Trace)
            traces_ = (await session.scalars(select_trace)).all()
            select_prompt = select(Prompt)
            prompts_ = (await session.scalars(select_prompt)).all()
            select_stdout = select(Stdout)
            stdouts_ = (await session.scalars(select_stdout)).all()
            session.expunge_all()

    assert repr(runs) == repr(runs_)
    traces = sorted(traces, key=lambda m: m.id)
    assert repr(traces) == repr(sorted(traces_, key=lambda m: m.id))
    prompts = sorted(prompts, key=lambda m: m.id)
    assert repr(prompts) == repr(sorted(prompts_, key=lambda m: m.id))
    stdouts = sorted(stdouts, key=lambda m: m.id)
    assert repr(stdouts) == repr(sorted(stdouts_, key=lambda m: m.id))
