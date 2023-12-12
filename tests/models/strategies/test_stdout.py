from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.models import Stdout
from nextline_rdb.models.strategies import (
    st_model_run,
    st_model_stdout,
    st_model_stdout_list,
    st_model_trace_list,
)
from nextline_rdb.utils.strategies import st_none_or


@given(st.data())
async def test_st_model_stdout(data: st.DataObject) -> None:
    stdout = data.draw(st_model_stdout())

    async with AsyncDB(use_migration=False) as db:
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


@given(st.data())
async def test_st_model_stdout_lists(data: st.DataObject) -> None:
    # generate_traces=False because that would generate stdout with traces
    if run := data.draw(st_none_or(st_model_run(generate_traces=False))):
        data.draw(st_none_or(st_model_trace_list(run=run, min_size=0, max_size=5)))
        assert run.traces is not None

    max_size = data.draw(st.integers(min_value=0, max_value=10))

    stdouts = data.draw(st_model_stdout_list(run=run, max_size=max_size))

    assert len(stdouts) <= max_size

    if stdouts:
        runs = set(stdout.trace.run for stdout in stdouts)
        assert len(runs) == 1
        assert run is None or run is runs.pop()

    async with AsyncDB(use_migration=False) as db:
        async with db.session.begin() as session:
            session.add_all(stdouts)

        async with db.session() as session:
            select_stdout = select(Stdout)
            stdouts_ = (await session.scalars(select_stdout)).all()
            session.expunge_all()
    stdouts = sorted(stdouts, key=lambda stdout: stdout.id)
    assert repr(stdouts) == repr(sorted(stdouts_, key=lambda stdout: stdout.id))
