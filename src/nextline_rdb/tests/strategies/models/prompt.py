from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.models import Trace, Prompt

from .trace import st_model_trace

MAX_INT = 2_147_483_647


@st.composite
def st_model_prompt(draw: st.DrawFn, trace: Optional[Trace] = None) -> Prompt:
    trace = trace or draw(st_model_trace())
    run_no = trace.run_no
    trace_no = trace.trace_no
    prompt_no = draw(st.integers(min_value=1, max_value=MAX_INT))
    open = draw(st.booleans())
    event = draw(st.text())
    started_at = draw(st.datetimes())
    file_name = draw(st.one_of(st.none(), st.text()))
    line_no = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=MAX_INT)))
    stdout = draw(st.one_of(st.none(), st.text()))
    command = draw(st.one_of(st.none(), st.text()))
    ended_at = draw(st.one_of(st.none(), st.datetimes()))
    model = Prompt(
        run_no=run_no,
        trace_no=trace_no,
        prompt_no=prompt_no,
        open=open,
        event=event,
        started_at=started_at,
        file_name=file_name,
        line_no=line_no,
        stdout=stdout,
        command=command,
        ended_at=ended_at,
        run=trace.run,
        trace=trace,
    )
    return model
