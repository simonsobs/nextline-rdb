from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run, st_model_run_list

from ...db import AsyncDB


@given(st.data())
async def test_st_model_run(data: st.DataObject) -> None:
    time = data.draw(st.one_of(st.none(), st.datetimes()))

    run = data.draw(st_model_run(time=time))
    assert run

    if time and run.started_at:
        assert time < run.started_at
    if time and run.ended_at:
        assert time < run.ended_at
    if run.started_at and run.ended_at:
        assert run.started_at < run.ended_at

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
    max_n_runs = data.draw(st.integers(min_value=0, max_value=10))
    runs = data.draw(st_model_run_list(max_size=max_n_runs))
    assert len(runs) <= max_n_runs
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
