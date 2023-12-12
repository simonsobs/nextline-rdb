from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.models import Prompt, Run, Stdout, Trace
from nextline_rdb.models.strategies import st_model_run, st_model_run_list
from nextline_rdb.utils import safe_compare as sc
from nextline_rdb.utils.strategies import (
    st_datetimes,
    st_graphql_ints,
    st_none_or,
    st_ranges,
)


@given(st.data())
@settings(max_examples=200)
async def test_st_model_run(data: st.DataObject) -> None:
    run_no = data.draw(st_none_or(st_graphql_ints(min_value=1)))
    if run_no is None:
        min_run_no, max_run_no = data.draw(st_ranges(st_=st_graphql_ints, min_start=1))
    else:
        min_run_no, max_run_no = None, None

    min_started_at, max_started_at = data.draw(st_ranges(st_=st_datetimes))
    min_ended_at, max_ended_at = data.draw(
        st_ranges(st_=st_datetimes, min_start=min_started_at)
    )

    generate_traces = data.draw(st.booleans())

    run = data.draw(
        st_model_run(
            run_no=run_no,
            min_run_no=min_run_no,
            max_run_no=max_run_no,
            min_started_at=min_started_at,
            max_started_at=max_started_at,
            min_ended_at=min_ended_at,
            max_ended_at=max_ended_at,
            generate_traces=generate_traces,
        )
    )

    if run_no is not None:
        assert run.run_no == run_no
    else:
        assert sc(min_run_no) <= run.run_no <= sc(max_run_no)

    assert sc(min_started_at) <= sc(run.started_at) <= sc(max_started_at)
    assert sc(min_ended_at) <= sc(run.ended_at) <= sc(max_ended_at)
    assert sc(run.started_at) <= sc(run.ended_at)

    if not run.started_at:
        assert not run.ended_at

    traces = run.traces
    prompts = run.prompts
    stdouts = run.stdouts
    if generate_traces:
        assert traces
    else:
        assert not traces
        assert not prompts
        assert not stdouts

    async with AsyncDB(use_migration=False) as db:
        async with db.session.begin() as session:
            session.add(run)
        async with db.session() as session:
            select_run = select(Run)
            run_ = await session.scalar(
                select_run.options(selectinload(Run.traces), selectinload(Run.prompts))
            )
            assert run_
            session.expunge_all()

    assert repr(run) == repr(run_)
    traces = sorted(traces, key=lambda trace: trace.id)
    assert repr(traces) == repr(sorted(run_.traces, key=lambda trace: trace.id))
    prompts = sorted(prompts, key=lambda prompt: prompt.id)
    assert repr(prompts) == repr(sorted(run_.prompts, key=lambda prompt: prompt.id))
    stdouts = sorted(stdouts, key=lambda stdout: stdout.id)


@given(st.data())
@settings(max_examples=200)
async def test_st_model_run_lists(data: st.DataObject) -> None:
    max_size = data.draw(st.integers(min_value=0, max_value=10))
    runs = data.draw(st_model_run_list(generate_traces=True, max_size=max_size))
    assert len(runs) <= max_size
    run_nos = [run.run_no for run in runs]
    assert run_nos == sorted(run_nos)

    traces = [trace for run in runs for trace in run.traces]
    prompts = [prompt for run in runs for prompt in run.prompts]
    stdouts = [stdout for run in runs for stdout in run.stdouts] 

    started_ats = [run.started_at for run in runs if run.started_at]
    assert started_ats == sorted(started_ats)

    async with AsyncDB(use_migration=False) as db:
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
    traces = sorted(traces, key=lambda trace: trace.id)
    assert repr(traces) == repr(sorted(traces_, key=lambda trace: trace.id))
    prompts = sorted(prompts, key=lambda prompt: prompt.id)
    assert repr(prompts) == repr(sorted(prompts_, key=lambda prompt: prompt.id))
    stdouts = sorted(stdouts, key=lambda stdout: stdout.id)
    assert repr(stdouts) == repr(sorted(stdouts_, key=lambda stdout: stdout.id))
