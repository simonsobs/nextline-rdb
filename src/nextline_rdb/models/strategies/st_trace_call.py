from collections.abc import Iterable
from typing import Callable, Optional, cast

from hypothesis import strategies as st

from nextline_test_utils.strategies import st_graphql_ints, st_none_or

from .. import Run, Trace, TraceCall
from .st_trace import st_model_trace
from .utils import st_started_at_ended_at


@st.composite
def st_model_trace_call(
    draw: st.DrawFn,
    trace_call_no: Optional[int] = None,
    trace: Optional[Trace] = None,
    generate_prompts: bool = False,
) -> TraceCall:
    from .st_prompt import st_model_prompt_list

    if trace is not None:
        # Unable to meet the unique constraints
        assert not generate_prompts

    trace = trace or draw(st_model_trace())
    if trace_call_no is None:
        trace_call_no = draw(st_graphql_ints(min_value=1))
    started_at, ended_at = draw(
        st_started_at_ended_at(
            min_start=trace.started_at,
            max_end=trace.ended_at,
            allow_start_none=False,
        )
    )
    file_name = draw(st_none_or(st.text()))
    line_no = draw(st_none_or(st_graphql_ints(min_value=1)))
    event = draw(st.text())
    model = TraceCall(
        trace_call_no=trace_call_no,
        started_at=started_at,
        file_name=file_name,
        line_no=line_no,
        event=event,
        ended_at=ended_at,
        run=trace.run,
        trace=trace,
    )

    if generate_prompts:
        draw(st_model_prompt_list(run=trace.run, min_size=1, max_size=10))

    return model


@st.composite
def st_model_trace_call_list(
    draw: st.DrawFn,
    run: Optional[Run] = None,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[TraceCall]:
    # NOTE: Unique constraint: (run_id, trace_call_no)
    run = run or draw(st_model_trace()).run

    if not run.traces:
        return []

    trace_call_nos = draw(
        st.lists(
            st_graphql_ints(min_value=1),
            min_size=min_size,
            max_size=max_size,
            unique=True,
        ).map(cast(Callable[[Iterable[int]], list[int]], sorted))
    )

    size = len(trace_call_nos)

    traces = draw(st.lists(st.sampled_from(run.traces), min_size=size, max_size=size))

    trace_calls = list[TraceCall]()
    for trace, trace_call_no in zip(traces, trace_call_nos):
        trace_call = draw(st_model_trace_call(trace_call_no=trace_call_no, trace=trace))
        trace_calls.append(trace_call)
    return trace_calls
