from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Run
from nextline_rdb.models.strategies import (
    SQLITE_INT_MAX,
    st_datetimes,
    st_model_run,
    st_model_run_list,
    st_none_or,
    st_sqlite_ints,
)

from ...db import AsyncDB


@given(st.data())
async def test_st_model_run(data: st.DataObject) -> None:
    min_run_no = data.draw(st_none_or(st_sqlite_ints(min_value=1)), label='min_run_no')

    max_run_no = data.draw(
        st_none_or(st_sqlite_ints(min_value=min_run_no or 1)), label='max_run_no'
    )

    min_started_at = data.draw(st_none_or(st_datetimes()), label='min_started_at')

    max_started_at = data.draw(
        st_none_or(st_datetimes(min_value=min_started_at)), label='max_started_at'
    )

    min_ended_at = data.draw(
        st_none_or(st_datetimes(min_value=min_started_at)), label='min_ended_at'
    )

    min_max_ended_at = (
        max(min_started_at, min_ended_at)
        if min_started_at and min_ended_at
        else (min_started_at or min_ended_at)
    )

    max_ended_at = data.draw(
        st_none_or(st_datetimes(min_value=min_max_ended_at)), label='max_ended_at'
    )

    run = data.draw(
        st_model_run(
            min_run_no=min_run_no,
            max_run_no=max_run_no,
            min_started_at=min_started_at,
            max_started_at=max_started_at,
            min_ended_at=min_ended_at,
            max_ended_at=max_ended_at,
        )
    )

    if min_run_no is None:
        assert 1 <= run.run_no
    else:
        assert min_run_no <= run.run_no

    if max_run_no is None:
        assert run.run_no <= SQLITE_INT_MAX
    else:
        assert run.run_no <= max_run_no

    if min_started_at and run.started_at:
        assert min_started_at <= run.started_at

    if max_started_at and run.started_at:
        assert run.started_at <= max_started_at

    if min_ended_at and run.ended_at:
        assert min_ended_at <= run.ended_at

    if max_ended_at and run.ended_at:
        assert run.ended_at <= max_ended_at

    if run.started_at and run.ended_at:
        assert run.started_at <= run.ended_at

    if not run.started_at:
        assert not run.ended_at

    async with AsyncDB() as db:
        async with db.session.begin() as session:
            session.add(run)
        async with db.session() as session:
            stmt = select(Run)
            run_ = await session.scalar(stmt)
            session.expunge_all()
    assert repr(run) == repr(run_)


@given(st.data())
async def test_st_model_run_lists(data: st.DataObject) -> None:
    max_size = data.draw(st.integers(min_value=0, max_value=10))
    runs = data.draw(st_model_run_list(max_size=max_size))
    assert len(runs) <= max_size
    run_nos = [run.run_no for run in runs]
    assert run_nos == sorted(run_nos)

    times_ = [(run.started_at, run.ended_at) for run in runs]
    times = [time for t_ in times_ for time in t_ if time]
    assert times == sorted(times)

    async with AsyncDB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)

        async with db.session() as session:
            stmt = select(Run)
            runs_ = (await session.scalars(stmt)).all()
            session.expunge_all()

    assert repr(runs) == repr(runs_)
