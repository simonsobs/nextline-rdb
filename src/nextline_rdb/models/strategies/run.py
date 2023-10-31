import datetime as dt
from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.models import Run

MAX_INT = 2_147_483_647


@st.composite
def st_model_run(
    draw: st.DrawFn,
    prev: Optional[Run] = None,
    time: Optional[dt.datetime] = None,
) -> Run | None:
    if prev and prev.run_no >= MAX_INT:
        return None
    min_run_no = prev.run_no + 1 if prev else 1
    min_started_at = time + dt.timedelta(seconds=1) if time else dt.datetime.min
    run_no = draw(st.integers(min_value=min_run_no, max_value=MAX_INT))
    state = draw(st.one_of(st.none(), st.text()))
    started_at = draw(st.one_of(st.none(), st.datetimes(min_value=min_started_at)))
    ended_at = (
        None
        if started_at is None
        else draw(st.one_of(st.none(), st.datetimes(min_value=started_at)))
    )
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
