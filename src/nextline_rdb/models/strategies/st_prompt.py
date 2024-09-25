from collections.abc import Iterable
from typing import Callable, Optional, cast

from hypothesis import strategies as st

from nextline_test_utils.strategies import st_graphql_ints, st_none_or

from .. import Prompt, Run, TraceCall
from .st_trace_call import st_model_trace_call
from .utils import st_started_at_ended_at


@st.composite
def st_model_prompt(
    draw: st.DrawFn,
    prompt_no: Optional[int] = None,
    trace_call: Optional[TraceCall] = None,
) -> Prompt:
    trace_call = trace_call or draw(st_model_trace_call())
    if prompt_no is None:
        prompt_no = draw(st_graphql_ints(min_value=1))
    open = draw(st.booleans())
    started_at, ended_at = draw(
        st_started_at_ended_at(
            min_start=trace_call.started_at,
            max_end=trace_call.ended_at,
            allow_start_none=False,
        )
    )
    stdout = draw(st_none_or(st.text()))
    command = draw(st_none_or(st.text()))
    model = Prompt(
        prompt_no=prompt_no,
        open=open,
        started_at=started_at,
        stdout=stdout,
        command=command,
        ended_at=ended_at,
        run=trace_call.run,
        trace=trace_call.trace,
        trace_call=trace_call,
    )
    return model


@st.composite
def st_model_prompt_list(
    draw: st.DrawFn,
    run: Optional[Run] = None,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Prompt]:
    # NOTE: Unique constraint: (run_id, prompt_no)
    run = run or draw(st_model_trace_call()).run

    if not run.trace_calls:
        return []

    prompt_nos = draw(
        st.lists(
            st_graphql_ints(min_value=1),
            min_size=min_size,
            max_size=max_size,
            unique=True,
        ).map(cast(Callable[[Iterable[int]], list[int]], sorted))
    )

    size = len(prompt_nos)

    trace_calls = draw(
        st.lists(st.sampled_from(run.trace_calls), min_size=size, max_size=size)
    )

    prompts = list[Prompt]()
    for trace_call, prompt_no in zip(trace_calls, prompt_nos):
        prompt = draw(st_model_prompt(prompt_no=prompt_no, trace_call=trace_call))
        prompts.append(prompt)
    return prompts
