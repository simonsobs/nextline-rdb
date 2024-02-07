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
    generate_script: bool = True,
    generate_traces: bool = True,
) -> Run:
    '''A strategy for `Run` models.

    Note on `generate_script`: If `script` is `None` and `generate_script` is
    `True`, a new `Script` model might be generated. If `script` is not `None`,
    `generate_script` is ignored.
    '''
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

    if script is None and generate_script:
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
    scripts: list[Script] | None = None,
) -> list[Run]:
    run_nos = draw(_st_run_nos(min_size=min_size, max_size=max_size))

    st_scripts = (
        _st_script_list(size=len(run_nos))
        if scripts is None
        else _st_script_list_choose_from(scripts, len(run_nos))
    )
    scripts_for_runs = draw(st_scripts)

    runs = list[Run]()
    min_started_at = None
    for run_no, script in zip(run_nos, scripts_for_runs):
        min_started_at = min_started_at or draw(st_datetimes())
        run = draw(
            st_model_run(
                run_no=run_no,
                script=script,
                generate_script=False,
                generate_traces=generate_traces,
                min_started_at=min_started_at,
            )
        )
        assert run.run_no == run_no

        if run.started_at is not None:
            min_started_at = run.started_at + dt.timedelta(seconds=1)
        # if run.ended_at is not None:
        #     min_started_at = run.ended_at + dt.timedelta(seconds=1)
        runs.append(run)
    return runs


def _st_run_nos(min_size: int, max_size: int | None) -> st.SearchStrategy[list[int]]:
    return st.lists(
        st_graphql_ints(min_value=1),
        min_size=min_size,
        max_size=max_size,
        unique=True,
    ).map(cast(Callable[[Iterable[int]], list[int]], sorted))


@st.composite
def _st_script_list_choose_from(
    draw: st.DrawFn, scripts: list[Script], size: int
) -> list[Script | None]:
    ret = list[Script | None]()
    for _ in mark_last(range(size)):
        if scripts:
            script = draw(
                st.one_of(
                    st.none(),
                    st.sampled_from(scripts),
                )
            )
        else:
            script = draw(st.none())
        ret.append(script)
    return ret


@st.composite
def _st_script_list(draw: st.DrawFn, size: int) -> list[Script | None]:
    from .st_script import st_model_script

    scripts = list[Script]()
    ret = list[Script | None]()
    for last, _ in mark_last(range(size)):
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

        if script is not None:
            script.current = last

        ret.append(script)
    return ret
