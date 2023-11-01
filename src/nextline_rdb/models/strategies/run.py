import datetime as dt
from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.models import Run

from .utils import st_datetimes, st_none_or, st_sqlite_ints


@st.composite
def st_model_run(
    draw: st.DrawFn,
    min_run_no: Optional[int] = None,
    max_run_no: Optional[int] = None,
    min_started_at: Optional[dt.datetime] = None,
    max_started_at: Optional[dt.datetime] = None,
    min_ended_at: Optional[dt.datetime] = None,
    max_ended_at: Optional[dt.datetime] = None,
) -> Run:
    # Validate options
    if min_run_no is None:
        min_run_no = 1

    min_started_at = min_started_at or dt.datetime.min
    max_started_at = max_started_at or dt.datetime.max
    min_ended_at = min_ended_at or dt.datetime.min
    max_ended_at = max_ended_at or dt.datetime.max
    assert min_started_at <= max_started_at
    assert min_started_at <= max_ended_at
    max_started_at = min(max_started_at, max_ended_at)
    min_ended_at = max(min_started_at, min_ended_at)
    assert min_ended_at <= max_ended_at

    # Generate model arguments
    run_no = draw(st_sqlite_ints(min_value=min_run_no, max_value=max_run_no))

    state = draw(st_none_or(st.text()))

    started_at = draw(
        st_none_or(st_datetimes(min_value=min_started_at, max_value=max_started_at))
    )
    if started_at:
        min_ended_at = max(started_at, min_ended_at)
    assert min_ended_at <= max_ended_at
    ended_at = (
        None
        if started_at is None
        else draw(
            st_none_or(st_datetimes(min_value=min_ended_at, max_value=max_ended_at))
        )
    )

    script = draw(st_none_or(st.text()))

    exception = draw(st_none_or(st.text()))

    # Create model
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
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Run]:
    run_nos = draw(
        st.lists(
            st_sqlite_ints(min_value=1),
            min_size=min_size,
            max_size=max_size,
            unique=True,
        ).map(sorted)
    )
    runs = list[Run]()
    min_started_at = draw(st_datetimes())
    for run_no in run_nos:
        run = draw(
            st_model_run(
                min_run_no=run_no, max_run_no=run_no, min_started_at=min_started_at
            )
        )
        if run.started_at is not None:
            min_started_at = run.started_at + dt.timedelta(seconds=1)
        if run.ended_at is not None:
            min_started_at = run.ended_at + dt.timedelta(seconds=1)
        runs.append(run)
    return runs
