import datetime

from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.models import Run

from .funcs import DB


@st.composite
def st_run(draw: st.DrawFn):
    run_no = draw(st.integers(min_value=1, max_value=2_147_483_647))
    state = draw(st.one_of(st.none(), st.text()))
    started_at = draw(st.one_of(st.none(), st.datetimes()))
    ended_at = draw(st.one_of(st.none(), st.datetimes()))
    script = draw(st.one_of(st.none(), st.text()))
    exception = draw(st.one_of(st.none(), st.text()))
    model = Run(
        run_no=run_no,
        state=state,
        started_at=started_at,
        ended_at=ended_at,
        script=script,
        exception=exception,
    )
    return model


@given(st.data())
async def test_repr(data: st.DataObject):
    async with DB() as Session:
        async with (Session() as session, session.begin()):
            model = data.draw(st_run())
            session.add(model)

        async with Session() as session:
            rows = await session.scalars(select(Run))
            for row in rows:
                repr_ = repr(row)
                assert Run, datetime
                assert repr_ == repr(eval(repr_))
