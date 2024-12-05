from typing import Optional, TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_test_utils.strategies import st_graphql_ints, st_none_or

from ... import Model, TraceCall
from .. import st_model_prompt, st_model_trace_call
from .funcs import assert_model_persistence


class StModelPromptKwargs(TypedDict, total=False):
    prompt_no: Optional[int]
    trace_call: Optional[TraceCall]


@st.composite
def st_st_model_prompt_kwargs(draw: st.DrawFn) -> StModelPromptKwargs:
    kwargs = StModelPromptKwargs()

    if draw(st.booleans()):
        kwargs['prompt_no'] = draw(st_none_or(st_graphql_ints(min_value=1)))

    if draw(st.booleans()):
        kwargs['trace_call'] = draw(
            st_none_or(st_model_trace_call(generate_prompts=False))
        )

    return kwargs


@given(kwargs=st_st_model_prompt_kwargs())
def test_st_model_prompt_kwargs(kwargs: StModelPromptKwargs) -> None:
    del kwargs


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(data=st.data())
def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_prompt_kwargs())

    # Call the strategy to be tested
    prompt = data.draw(st_model_prompt(**kwargs))

    # Assert the generated values
    prompt_no = kwargs.get('prompt_no')
    trace_call = kwargs.get('trace_call')

    if prompt_no is not None:
        assert prompt.prompt_no == prompt_no

    if trace_call is not None:
        assert prompt.trace_call == trace_call


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_prompt())
async def test_db(instance: Model) -> None:
    await assert_model_persistence([instance])
