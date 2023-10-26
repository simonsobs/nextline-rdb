from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.models import Stdout, Trace

from .trace import st_model_trace

MAX_INT = 2_147_483_647


@st.composite
def st_model_stdout(draw: st.DrawFn, trace: Optional[Trace] = None) -> Stdout:
    trace = trace or draw(st_model_trace())
    run_no = trace.run_no
    trace_no = trace.trace_no
    text = draw(st.text())
    written_at = draw(st.datetimes())
    model = Stdout(
        run_no=run_no,
        trace_no=trace_no,
        text=text,
        written_at=written_at,
        run=trace.run,
        trace=trace,
    )
    return model
