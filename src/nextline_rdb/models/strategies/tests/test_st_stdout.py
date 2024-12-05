from typing import Optional, TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_test_utils.strategies import st_none_or

from ... import Model, Trace
from .. import st_model_stdout, st_model_trace
from .funcs import assert_model_persistence


class StModelStdoutKwargs(TypedDict, total=False):
    trace: Optional[Trace]


@st.composite
def st_st_model_stdout_kwargs(draw: st.DrawFn) -> StModelStdoutKwargs:
    kwargs = StModelStdoutKwargs()

    if draw(st.booleans()):
        kwargs['trace'] = draw(st_none_or(st_model_trace()))

    return kwargs


@given(kwargs=st_st_model_stdout_kwargs())
def test_st_model_prompt_kwargs(kwargs: StModelStdoutKwargs) -> None:
    del kwargs


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(data=st.data())
def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_stdout_kwargs())

    # Call the strategy to be tested
    stdout = data.draw(st_model_stdout(**kwargs))

    # Assert the generated values
    trace = kwargs.get('trace')

    if trace is not None:
        assert stdout.trace == trace


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_stdout())
async def test_db(instance: Model) -> None:
    await assert_model_persistence([instance])
