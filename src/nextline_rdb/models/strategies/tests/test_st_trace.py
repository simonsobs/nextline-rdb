from typing import Optional, TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_graphql_ints, st_none_or

from ... import Model, Run
from .. import st_model_run, st_model_trace, st_thread_task_no
from .funcs import assert_model_persistence


class StModelTraceKwargs(TypedDict, total=False):
    run: Optional[Run]
    trace_no: Optional[int]
    thread_task_no: Optional[tuple[int, int | None]]
    generate_trace_calls: bool
    generate_prompts: bool


@st.composite
def st_st_model_trace_kwargs(draw: st.DrawFn) -> StModelTraceKwargs:
    kwargs = StModelTraceKwargs()

    if draw(st.booleans()):
        kwargs['run'] = draw(st_none_or(st_model_run(generate_traces=False)))

    if draw(st.booleans()):
        kwargs['trace_no'] = draw(st_none_or(st_graphql_ints(min_value=1)))

    if draw(st.booleans()):
        kwargs['thread_task_no'] = draw(st_none_or(st_thread_task_no()))

    if kwargs.get('run') is None and draw(st.booleans()):
        kwargs['generate_trace_calls'] = draw(st.booleans())

    if kwargs.get('generate_trace_calls', False) and draw(st.booleans()):
        kwargs['generate_prompts'] = draw(st.booleans())

    return kwargs


@given(kwargs=st_st_model_trace_kwargs())
def test_st_model_trace_kwargs(kwargs: StModelTraceKwargs) -> None:
    if kwargs.get('run') is not None:
        assert not kwargs.get('generate_trace_calls')
        assert not kwargs.get('generate_prompts')

    if not kwargs.get('generate_trace_calls', False):
        assert not kwargs.get('generate_prompts')


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(data=st.data())
def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_trace_kwargs())

    # Call the strategy to be tested
    trace = data.draw(st_model_trace(**kwargs))

    # Assert the generated values
    run = kwargs.get('run')
    trace_no = kwargs.get('trace_no')
    thread_task_no = kwargs.get('thread_task_no')
    generate_trace_calls = kwargs.get('generate_trace_calls', False)
    generate_prompts = kwargs.get('generate_prompts', False)

    assert run is None or run is trace.run
    run = trace.run

    assert trace_no is None or trace_no == trace.trace_no
    assert thread_task_no is None or thread_task_no == (trace.thread_no, trace.task_no)

    assert sc(run.started_at) <= trace.started_at
    assert trace.started_at <= sc(trace.ended_at)
    assert sc(trace.ended_at) <= sc(run.ended_at)

    assert not generate_trace_calls or trace.trace_calls
    assert not generate_prompts or trace.prompts


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_trace())
async def test_db(instance: Model) -> None:
    await assert_model_persistence([instance])
