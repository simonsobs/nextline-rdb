from collections.abc import Iterable
from typing import Callable, Optional, cast

from hypothesis import strategies as st

from nextline_rdb.models import Prompt, Trace
from nextline_rdb.utils.strategies import st_none_or, st_sqlite_ints

from .trace import st_model_trace
from .utils import st_started_at_ended_at


@st.composite
def st_model_prompt(
    draw: st.DrawFn,
    prompt_no: Optional[int] = None,
    trace: Optional[Trace] = None,
) -> Prompt:
    trace = trace or draw(st_model_trace(generate_prompts=False))
    run_no = trace.run_no
    trace_no = trace.trace_no
    if prompt_no is None:
        prompt_no = draw(st_sqlite_ints(min_value=1))
    open = draw(st.booleans())
    event = draw(st.text())
    started_at, ended_at = draw(
        st_started_at_ended_at(
            min_start=trace.started_at,
            max_end=trace.ended_at,
            allow_start_none=False,
        )
    )
    file_name = draw(st_none_or(st.text()))
    line_no = draw(st_none_or(st_sqlite_ints(min_value=1)))
    stdout = draw(st_none_or(st.text()))
    command = draw(st_none_or(st.text()))
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


@st.composite
def st_model_prompt_list(
    draw: st.DrawFn,
    trace: Optional[Trace] = None,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Prompt]:
    trace = trace or draw(st_model_trace(generate_prompts=False))

    prompt_nos = draw(
        st.lists(
            st_sqlite_ints(min_value=1),
            min_size=min_size,
            max_size=max_size,
            unique=True,
        ).map(cast(Callable[[Iterable[int]], list[int]], sorted))
    )

    prompts = list[Prompt]()
    for prompt_no in prompt_nos:
        prompt = draw(st_model_prompt(prompt_no=prompt_no, trace=trace))
        prompts.append(prompt)
    return prompts
