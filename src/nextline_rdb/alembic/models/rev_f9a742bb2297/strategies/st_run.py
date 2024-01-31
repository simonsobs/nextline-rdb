import datetime as dt
from collections.abc import Iterable
from typing import Callable, Optional, cast

from hypothesis import strategies as st

from nextline_rdb.utils import mark_last
from nextline_rdb.utils.strategies import st_datetimes, st_graphql_ints, st_none_or

from .. import Run, Script
from .utils import st_started_at_ended_at


@st.composite
def st_model_run(
    draw: st.DrawFn,
    run_no: Optional[int] = None,
    min_run_no: Optional[int] = None,
    max_run_no: Optional[int] = None,
    min_started_at: Optional[dt.datetime] = None,
    max_started_at: Optional[dt.datetime] = None,
    min_ended_at: Optional[dt.datetime] = None,
    max_ended_at: Optional[dt.datetime] = None,
    script: Optional[Script] = None,
    generate_traces: bool = True,
) -> Run:
    from .st_prompt import st_model_prompt_list
    from .st_script import st_model_script
    from .st_stdout import st_model_stdout_list
    from .st_trace import st_model_trace_list

    def st_run_no() -> st.SearchStrategy[int]:
        if run_no is not None:
            return st.just(run_no)
        min_ = min_run_no if min_run_no is not None else 1
        return st_graphql_ints(min_value=min_, max_value=max_run_no)

    run_no = draw(st_run_no())

    state = draw(st_none_or(st.text()))

    started_at, ended_at = draw(
        st_started_at_ended_at(
            min_start=min_started_at,
            max_start=max_started_at,
            min_end=min_ended_at,
            max_end=max_ended_at,
        )
    )

    if script is None:
        script = draw(st_none_or(st_model_script()))

    exception = draw(st_none_or(st.text()))

    run = Run(
        run_no=run_no,
        state=state,
        started_at=started_at,
        ended_at=ended_at,
        script=script,
        exception=exception,
    )

    if generate_traces:
        draw(st_model_trace_list(run=run, min_size=1, max_size=4))
        draw(st_model_prompt_list(run=run, min_size=0, max_size=8))
        draw(st_model_stdout_list(run=run, min_size=0, max_size=5))

    return run


@st.composite
def st_model_run_list(
    draw: st.DrawFn,
    generate_traces: bool = False,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Run]:
    from .st_script import st_model_script

    run_nos = draw(
        st.lists(
            st_graphql_ints(min_value=1),
            min_size=min_size,
            max_size=max_size,
            unique=True,
        ).map(cast(Callable[[Iterable[int]], list[int]], sorted))
    )

    runs = list[Run]()
    scripts = list[Script]()
    min_started_at = None
    for last, run_no in mark_last(run_nos):
        min_started_at = min_started_at or draw(st_datetimes())

        if scripts:
            script = draw(
                st.one_of(
                    st_none_or(st_model_script(current=False)),
                    st.sampled_from(scripts),
                )
            )
        else:
            script = draw(st_none_or(st_model_script(current=False)))
            if script is not None:
                scripts.append(script)

        run = draw(
            st_model_run(
                run_no=run_no,
                script=script,
                generate_traces=generate_traces,
                min_started_at=min_started_at,
            )
        )
        assert run.run_no == run_no

        if run.script is not None:
            run.script.current = last

        if run.started_at is not None:
            min_started_at = run.started_at + dt.timedelta(seconds=1)
        # if run.ended_at is not None:
        #     min_started_at = run.ended_at + dt.timedelta(seconds=1)
        runs.append(run)
    return runs
