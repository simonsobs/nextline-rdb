from typing import Optional, TypedDict

from hypothesis import Phase, given, note, settings
from hypothesis import strategies as st

from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_none_or, st_ranges

from ... import Model, Run
from .. import (
    st_model_prompt_list,
    st_model_run,
    st_model_trace_call_list,
    st_model_trace_list,
)
from .funcs import assert_model_persistence


class StModelPromptListKwargs(TypedDict, total=False):
    run: Optional[Run]
    min_size: int
    max_size: Optional[int]


@st.composite
def st_st_model_prompt_list_kwargs(draw: st.DrawFn) -> StModelPromptListKwargs:
    kwargs = StModelPromptListKwargs()

    if draw(st.booleans()):
        # generate_traces=False because True would generate a trace with prompts
        run = draw(st_none_or(st_model_run(generate_traces=False)))
        kwargs['run'] = run
        if run:
            draw(st_none_or(st_model_trace_list(run=run, min_size=0, max_size=3)))
            draw(st_none_or(st_model_trace_call_list(run=run, min_size=0, max_size=5)))

    if draw(st.booleans()):
        min_size, max_size = draw(
            st_ranges(
                st.integers,
                min_start=0,
                max_end=4,
                allow_start_none=False,
                allow_end_none=False,
            )
        )
        assert isinstance(min_size, int)
        kwargs['min_size'] = min_size
        kwargs['max_size'] = max_size

    return kwargs


@given(kwargs=st_st_model_prompt_list_kwargs())
def test_st_model_prompt_list_kwargs(kwargs: StModelPromptListKwargs) -> None:
    assert sc(kwargs.get('min_size')) <= sc(kwargs.get('max_size'))


@settings(max_examples=500, phases=(Phase.generate,))  # Avoid shrinking
@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_prompt_list_kwargs())
    note(kwargs)

    # Call the strategy to be tested
    prompts = data.draw(st_model_prompt_list(**kwargs))

    # Assert the generated values
    run = kwargs.get('run')
    min_size = kwargs.get('min_size', 0)
    max_size = kwargs.get('max_size')

    if run and not run.trace_calls:
        # `prompts` is not generated if `run` with no `trace_calls` is provided
        assert not prompts
    else:
        assert min_size <= len(prompts) <= sc(max_size)

    if prompts:
        runs = set(prompt.trace.run for prompt in prompts)
        assert len(runs) == 1
        assert run is None or run is runs.pop()


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instances=st_model_prompt_list(max_size=5))
async def test_db(instances: list[Model]) -> None:
    await assert_model_persistence(instances)
