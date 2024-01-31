from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.utils.strategies import st_datetimes

from .. import Run, Stdout, Trace
from .st_trace import st_model_trace


@st.composite
def st_model_stdout(draw: st.DrawFn, trace: Optional[Trace] = None) -> Stdout:
    trace = trace or draw(st_model_trace())
    run_no = trace.run_no
    trace_no = trace.trace_no
    text = draw(st.text())
    written_at = draw(st_datetimes())
    stdout = Stdout(
        run_no=run_no,
        trace_no=trace_no,
        text=text,
        written_at=written_at,
        run=trace.run,
        trace=trace,
    )
    return stdout


@st.composite
def st_model_stdout_list(
    draw: st.DrawFn,
    run: Optional[Run] = None,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Stdout]:
    run = run or draw(st_model_trace()).run

    traces = (
        draw(
            st.lists(st.sampled_from(run.traces), min_size=min_size, max_size=max_size)
        )
        if run.traces
        else []
    )

    stdouts = list[Stdout]()
    for trace in traces:
        stdout = draw(st_model_stdout(trace=trace))
        stdouts.append(stdout)

    return stdouts
