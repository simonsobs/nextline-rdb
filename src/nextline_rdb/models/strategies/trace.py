from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.models import Run, Trace
from nextline_rdb.utils.strategies import st_sqlite_ints

from .run import st_model_run
from .utils import st_started_at_ended_at

MAX_INT = 2_147_483_647


@st.composite
def st_model_trace(draw: st.DrawFn, run: Optional[Run] = None) -> Trace:
    run = run or draw(st_model_run())
    run_no = run.run_no
    trace_no = draw(st_sqlite_ints(min_value=1))
    state = draw(st.text())
    thread_no = draw(st_sqlite_ints(min_value=1))
    task_no = draw(st.one_of(st.none(), st_sqlite_ints(min_value=1)))
    started_at, ended_at = draw(
        st_started_at_ended_at(
            min_start=run.started_at,
            max_end=run.ended_at,
            allow_start_none=False,
        )
    )
    model = Trace(
        run_no=run_no,
        trace_no=trace_no,
        state=state,
        thread_no=thread_no,
        task_no=task_no,
        started_at=started_at,
        ended_at=ended_at,
        run=run,
    )
    return model
