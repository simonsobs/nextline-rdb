from typing import Optional, TypedDict

from hypothesis import Phase, given, note, settings
from hypothesis import strategies as st

from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_ranges

from ... import Model
from .. import st_model_script_list
from .funcs import assert_model_persistence


class StModelScriptListKwargs(TypedDict, total=False):
    min_size: int
    max_size: Optional[int]


@st.composite
def st_st_model_script_list_kwargs(draw: st.DrawFn) -> StModelScriptListKwargs:
    kwargs = StModelScriptListKwargs()

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


@given(kwargs=st_st_model_script_list_kwargs())
def test_st_model_script_list_kwargs(kwargs: StModelScriptListKwargs) -> None:
    assert sc(kwargs.get('min_size')) <= sc(kwargs.get('max_size'))


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_script_list_kwargs())
    note(kwargs)

    # Call the strategy to be tested
    scripts = data.draw(st_model_script_list(**kwargs))

    # Assert the generated values
    min_size = kwargs.get('min_size', 0)
    max_size = kwargs.get('max_size')

    assert sc(min_size) <= len(scripts) <= sc(max_size)

    current_scripts = {script for script in scripts if script.current}
    assert len(current_scripts) <= 1


@given(instances=st_model_script_list(min_size=0, max_size=3))
async def test_db(instances: list[Model]) -> None:
    await assert_model_persistence(instances)
