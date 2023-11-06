from collections.abc import Iterable
from typing import Callable, Optional, cast

from hypothesis import strategies as st

from nextline_rdb.models import Run, Trace
from nextline_rdb.utils.strategies import st_none_or, st_sqlite_ints

from .run import st_model_run
from .utils import st_started_at_ended_at


@st.composite
def st_model_trace(
    draw: st.DrawFn,
    run: Optional[Run] = None,
    trace_no: Optional[int] = None,
    thread_task_no: Optional[tuple[int, int | None]] = None,
) -> Trace:
    run = run or draw(st_model_run())
    run_no = run.run_no

    if trace_no is None:
        trace_no = draw(st_sqlite_ints(min_value=1))

    state = draw(st.text())

    thread_task_no = thread_task_no or draw(st_thread_task_no())
    thread_no, task_no = thread_task_no

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


def st_thread_task_no() -> st.SearchStrategy[tuple[int, int | None]]:
    return st.tuples(
        st_sqlite_ints(min_value=1),
        st_none_or(st_sqlite_ints(min_value=1)),
    )


def sort_thread_task_nos(
    thread_task_nos: Iterable[tuple[int, int | None]]
) -> list[tuple[int, int | None]]:
    return sorted(thread_task_nos, key=lambda x: (x[0], x[1] or 0))


@st.composite
def st_model_trace_list(
    draw: st.DrawFn,
    run: Optional[Run] = None,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Trace]:
    run = run or draw(st_model_run())
    thread_task_nos = draw(
        st.lists(
            st_thread_task_no(), min_size=min_size, max_size=max_size, unique=True
        ).map(sort_thread_task_nos)
    )
    trace_nos = draw(
        st.lists(
            st_sqlite_ints(min_value=1),
            min_size=len(thread_task_nos),
            max_size=len(thread_task_nos),
            unique=True,
        ).map(cast(Callable[[Iterable[int]], list[int]], sorted))
    )
    assert len(thread_task_nos) == len(trace_nos)
    traces = list[Trace]()
    for trace_no, thread_task_no in zip(trace_nos, thread_task_nos):
        trace = draw(
            st_model_trace(
                run=run,
                trace_no=trace_no,
                thread_task_no=thread_task_no,
            )
        )
        assert run is trace.run
        assert trace_no == trace.trace_no
        assert thread_task_no == (trace.thread_no, trace.task_no)
        traces.append(trace)
    return traces
