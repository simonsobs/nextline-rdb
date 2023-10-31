import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Run
from nextline_rdb.tests.strategies.models import st_model_run

from ..db import AsyncDB


@given(st.data())
async def test_repr(data: st.DataObject):
    async with AsyncDB() as db:
        async with db.session.begin() as session:
            model = data.draw(st_model_run())
            session.add(model)

        async with db.session() as session:
            rows = await session.scalars(select(Run))
            for row in rows:
                repr_ = repr(row)
                assert Run, datetime  # type: ignore[truthy-function]
                assert repr_ == repr(eval(repr_))


@given(st.data())
async def test_st(data: st.DataObject):
    max_n_runs = 10
    async with AsyncDB() as db:
        async with db.session.begin() as session:
            prev: Run | None = None
            time: datetime.datetime | None = None
            n_runs = 0
            while True:
                if n_runs >= max_n_runs:
                    break
                if data.draw(st.booleans()):
                    break
                if (run := data.draw(st_model_run(prev=prev, time=time))) is None:
                    break
                match run:
                    case Run(started_at=None, ended_at=None):
                        pass
                    case Run(started_at=None, ended_at=ended_at):
                        assert ended_at is None
                    case Run(started_at=started_at, ended_at=None):
                        assert started_at is not None
                        if time is not None:
                            assert started_at > time
                        time = started_at
                    case Run(started_at=started_at, ended_at=ended_at):
                        assert started_at is not None
                        assert ended_at is not None
                        assert started_at < ended_at
                        if time is not None:
                            assert started_at > time
                        time = ended_at
                session.add(run)
                # ic(run)
                n_runs += 1
                prev = run
