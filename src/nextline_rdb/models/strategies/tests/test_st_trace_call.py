from typing import Optional, TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_test_utils.strategies import st_graphql_ints, st_none_or

from ... import Model, Trace
from .. import st_model_trace, st_model_trace_call
from .funcs import assert_model_persistence


class StModelTraceCallKwargs(TypedDict, total=False):
    trace_call_no: Optional[int]
    trace: Optional[Trace]
    generate_prompts: bool


@st.composite
def st_st_model_trace_call_kwargs(draw: st.DrawFn) -> StModelTraceCallKwargs:
    kwargs = StModelTraceCallKwargs()

    if draw(st.booleans()):
        kwargs['trace_call_no'] = draw(st_none_or(st_graphql_ints(min_value=1)))

    if draw(st.booleans()):
        kwargs['trace'] = draw(st_none_or(st_model_trace(generate_trace_calls=False)))

    if kwargs.get('trace') is None and draw(st.booleans()):
        kwargs['generate_prompts'] = draw(st.booleans())

    return kwargs


@given(kwargs=st_st_model_trace_call_kwargs())
def test_st_model_trace_call_kwargs(kwargs: StModelTraceCallKwargs) -> None:
    if kwargs.get('trace'):
        # Unable to meet the unique constraints
        assert not kwargs.get('generate_prompts')


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(data=st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_trace_call_kwargs())

    # Call the strategy to be tested
    trace_call = data.draw(st_model_trace_call(**kwargs))

    # Assert the generated values
    trace_call_no = kwargs.get('trace_call_no')
    trace = kwargs.get('trace')
    generate_prompts = kwargs.get('generate_prompts', False)

    if trace_call_no is not None:
        assert trace_call.trace_call_no == trace_call_no

    if trace is not None:
        assert trace_call.trace == trace

    if generate_prompts:
        assert trace_call.prompts


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_trace_call())
async def test_db(instance: Model) -> None:
    await assert_model_persistence([instance])
