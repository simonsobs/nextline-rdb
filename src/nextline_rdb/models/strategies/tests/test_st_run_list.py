from typing import TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_none_or, st_ranges

from ... import Model, Script
from .. import st_model_run_list, st_model_script_list
from .funcs import assert_model_persistence


class StModelRunListKwargs(TypedDict, total=False):
    generate_traces: bool
    min_size: int
    max_size: int
    scripts: list[Script] | None
    allow_started_at_none: bool


@st.composite
def st_st_model_run_list_kwargs(draw: st.DrawFn) -> StModelRunListKwargs:
    kwargs = StModelRunListKwargs()

    if draw(st.booleans()):
        kwargs['generate_traces'] = draw(st.booleans())

    max_size: int | None = None
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
        assert isinstance(max_size, int)
        kwargs['min_size'] = min_size
        kwargs['max_size'] = max_size

    if draw(st.booleans()):
        kwargs['scripts'] = draw(st_none_or(st_model_script_list(max_size=max_size)))

    if draw(st.booleans()):
        kwargs['allow_started_at_none'] = draw(st.booleans())

    return kwargs


@given(kwargs=st_st_model_run_list_kwargs())
def test_st_model_run_list_kwargs(kwargs: StModelRunListKwargs) -> None:
    assert sc(kwargs.get('min_size')) <= sc(kwargs.get('max_size'))


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_run_list_kwargs())

    # Call the strategy to be tested
    runs = data.draw(st_model_run_list(**kwargs))

    # Assert the generated values
    generate_traces = kwargs.get('generate_traces', False)
    min_size = kwargs.get('min_size', 0)
    max_size = kwargs.get('max_size')
    scripts = kwargs.get('scripts')
    allow_started_at_none = kwargs.get('allow_started_at_none', True)

    assert min_size <= len(runs) <= sc(max_size)
    run_nos = [run.run_no for run in runs]
    assert run_nos == sorted(run_nos)

    traces = [trace for run in runs for trace in run.traces]
    trace_calls = [trace_call for run in runs for trace_call in run.trace_calls]
    prompts = [prompt for run in runs for prompt in run.prompts]
    stdouts = [stdout for run in runs for stdout in run.stdouts]

    if generate_traces and runs:
        assert traces
        assert trace_calls
        assert prompts
        assert stdouts

    if not generate_traces:
        assert not traces
        assert not trace_calls
        assert not prompts
        assert not stdouts

    if not allow_started_at_none:
        assert all(run.started_at for run in runs)

    started_ats = [run.started_at for run in runs if run.started_at]
    assert started_ats == sorted(started_ats)

    scripts_ = {run.script for run in runs if run.script}
    current_script = {script for script in scripts_ if script.current}
    assert len(current_script) <= 1
    if scripts is not None:
        assert scripts_ <= set(scripts)


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instances=st_model_run_list(generate_traces=True, max_size=3))
async def test_db(instances: list[Model]) -> None:
    await assert_model_persistence(instances)
