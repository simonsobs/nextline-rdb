import datetime as dt
from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.models import Run
from nextline_rdb.utils.strategies import st_datetimes, st_none_or, st_sqlite_ints

from .utils import st_started_at_ended_at


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
    if min_run_no is None:
        min_run_no = 1

    run_no = draw(st_sqlite_ints(min_value=min_run_no, max_value=max_run_no))

    state = draw(st_none_or(st.text()))

    started_at, ended_at = draw(
        st_started_at_ended_at(
            min_start=min_started_at,
            max_start=max_started_at,
            min_end=min_ended_at,
            max_end=max_ended_at,
        )
    )

    script = draw(st_none_or(st.text()))

    exception = draw(st_none_or(st.text()))

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
