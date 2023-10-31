from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.models import Run, Trace

from .run import st_model_run

MAX_INT = 2_147_483_647


@st.composite
def st_model_trace(draw: st.DrawFn, run: Optional[Run] = None) -> Trace:
    run = run or draw(st_model_run())
    run_no = run.run_no
    trace_no = draw(st.integers(min_value=1, max_value=MAX_INT))
    state = draw(st.text())
    thread_no = draw(st.integers(min_value=1, max_value=MAX_INT))
    task_no = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=MAX_INT)))
    started_at = draw(st.datetimes())
    ended_at = draw(st.one_of(st.none(), st.datetimes()))
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
