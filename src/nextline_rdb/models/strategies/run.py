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


@st.composite
def st_model_run_list(
    draw: st.DrawFn,
    max_size: Optional[int] = None,
):
    runs = list[Run]()
    prev: Run | None = None
    time: dt.datetime | None = None
    n_runs = 0
    while True:
        if max_size is not None and n_runs >= max_size:
            break
        if draw(st.booleans()):
            break
        run = draw(st_model_run(prev=prev, time=time))
        if run is None:
            break
        if run.started_at is not None:
            time = run.started_at
        if run.ended_at is not None:
            time = run.ended_at
        runs.append(run)
        n_runs += 1
        prev = run
    return runs
