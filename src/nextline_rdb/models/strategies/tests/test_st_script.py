from typing import Optional, TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from ... import Model
from .. import st_model_script
from .funcs import assert_model_persistence


class StModelScriptKwargs(TypedDict, total=False):
    current: Optional[bool]


@st.composite
def st_st_model_script_kwargs(draw: st.DrawFn) -> StModelScriptKwargs:
    kwargs = StModelScriptKwargs()

    if draw(st.booleans()):
        kwargs['current'] = draw(st.booleans())

    return kwargs


@given(kwargs=st_st_model_script_kwargs())
def test_st_model_script_kwargs(kwargs: StModelScriptKwargs) -> None:
    del kwargs


@given(data=st.data())
def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_script_kwargs())

    # Call the strategy to be tested
    script = data.draw(st_model_script(**kwargs))

    # Assert the generated values
    current = kwargs.get('current')

    if current is not None:
        assert script.current == current

    compile(script.script, '<string>', 'exec')


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_script())
async def test_db(instance: Model) -> None:
    await assert_model_persistence([instance])
