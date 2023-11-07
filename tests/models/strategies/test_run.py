from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run, st_model_run_list
from nextline_rdb.utils import safe_compare as sc
from nextline_rdb.utils.strategies import (
    st_datetimes,
    st_none_or,
    st_ranges,
    st_sqlite_ints,
)

from ...db import AsyncDB


@given(st.data())
async def test_st_model_run(data: st.DataObject) -> None:
    run_no = data.draw(st_none_or(st_sqlite_ints(min_value=1)))
    if run_no is None:
        min_run_no, max_run_no = data.draw(st_ranges(st_=st_sqlite_ints(), min_start=1))
    else:
        min_run_no, max_run_no = None, None

    min_started_at, max_started_at = data.draw(st_ranges(st_=st_datetimes()))
    min_ended_at, max_ended_at = data.draw(
        st_ranges(st_=st_datetimes(), min_start=min_started_at)
    )

    run = data.draw(
        st_model_run(
            run_no=run_no,
            min_run_no=min_run_no,
            max_run_no=max_run_no,
            min_started_at=min_started_at,
            max_started_at=max_started_at,
            min_ended_at=min_ended_at,
            max_ended_at=max_ended_at,
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

    async with AsyncDB() as db:
        async with db.session.begin() as session:
            session.add(run)
        async with db.session() as session:
            select_run = select(Run)
            run_ = await session.scalar(select_run)
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
