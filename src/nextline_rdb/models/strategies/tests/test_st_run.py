from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB
from nextline_rdb.utils import safe_compare as sc
from nextline_rdb.utils.strategies import (
    st_datetimes,
    st_graphql_ints,
    st_none_or,
    st_ranges,
)

from ... import Model, Run
from .. import st_model_run


@given(st.data())
@settings(max_examples=200)
async def test_options(data: st.DataObject) -> None:
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

    if run.script:
        compile(run.script, '<string>', 'exec')


@given(run=st_model_run())
async def test_db(run: Run) -> None:
    traces = run.traces
    prompts = run.prompts
    stdouts = run.stdouts

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(run)
        async with db.session() as session:
            select_run = select(Run)
            run_ = await session.scalar(
                select_run.options(
                    selectinload(Run.traces),
                    selectinload(Run.prompts),
                    selectinload(Run.stdouts),
                )
            )
            assert run_
            session.expunge_all()

    assert repr(run) == repr(run_)
    traces = sorted(traces, key=lambda m: m.id)
    assert repr(traces) == repr(sorted(run_.traces, key=lambda m: m.id))
    prompts = sorted(prompts, key=lambda m: m.id)
    assert repr(prompts) == repr(sorted(run_.prompts, key=lambda m: m.id))
    stdouts = sorted(stdouts, key=lambda m: m.id)
    assert repr(stdouts) == repr(sorted(run_.stdouts, key=lambda m: m.id))
