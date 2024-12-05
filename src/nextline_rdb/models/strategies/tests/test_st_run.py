import datetime as dt
from typing import Optional, TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import (
    st_datetimes,
    st_graphql_ints,
    st_none_or,
    st_ranges,
)

from ... import Model, Script
from .. import st_model_run, st_model_script
from .funcs import assert_model_persistence


class StModelRunKwargs(TypedDict, total=False):
    run_no: Optional[int]
    min_run_no: Optional[int]
    max_run_no: Optional[int]
    min_started_at: Optional[dt.datetime]
    max_started_at: Optional[dt.datetime]
    min_ended_at: Optional[dt.datetime]
    max_ended_at: Optional[dt.datetime]
    script: Optional[Script]
    allow_started_at_none: bool
    generate_script: bool
    generate_traces: bool


@st.composite
def st_st_model_run_kwargs(draw: st.DrawFn) -> StModelRunKwargs:
    kwargs = StModelRunKwargs()

    if draw(st.booleans()):
        kwargs['run_no'] = draw(st_none_or(st_graphql_ints(min_value=1)))

    if kwargs.get('run_no') is None:
        min_run_no, max_run_no = draw(st_ranges(st_graphql_ints, min_start=1))
        if min_run_no is not None:
            kwargs['min_run_no'] = min_run_no
        if max_run_no is not None:
            kwargs['max_run_no'] = max_run_no

    min_started_at: Optional[dt.datetime] = None
    if draw(st.booleans()):
        min_started_at, max_started_at = draw(st_ranges(st_datetimes))
        kwargs['min_started_at'] = min_started_at
        kwargs['max_started_at'] = max_started_at

    if draw(st.booleans()):
        min_ended_at, max_ended_at = draw(
            st_ranges(st_datetimes, min_start=min_started_at)
        )
        kwargs['min_ended_at'] = min_ended_at
        kwargs['max_ended_at'] = max_ended_at

    if draw(st.booleans()):
        kwargs['script'] = draw(st_none_or(st_model_script()))

    if draw(st.booleans()):
        kwargs['allow_started_at_none'] = draw(st.booleans())

    if draw(st.booleans()):
        kwargs['generate_script'] = draw(st.booleans())

    if draw(st.booleans()):
        kwargs['generate_traces'] = draw(st.booleans())

    return kwargs


@given(kwargs=st_st_model_run_kwargs())
def test_st_st_model_run_kwargs(kwargs: StModelRunKwargs) -> None:
    assert sc(kwargs.get('min_run_no')) <= sc(kwargs.get('max_run_no'))
    assert sc(kwargs.get('min_started_at')) <= sc(kwargs.get('max_started_at'))
    assert sc(kwargs.get('min_started_at')) <= sc(kwargs.get('min_ended_at'))
    assert sc(kwargs.get('min_ended_at')) <= sc(kwargs.get('max_ended_at'))


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(data=st.data())
def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_run_kwargs())

    # Call the strategy to be tested
    run = data.draw(st_model_run(**kwargs))

    # Assert the generated values
    run_no = kwargs.get('run_no')
    min_run_no = kwargs.get('min_run_no')
    max_run_no = kwargs.get('max_run_no')
    min_started_at = kwargs.get('min_started_at')
    max_started_at = kwargs.get('max_started_at')
    min_ended_at = kwargs.get('min_ended_at')
    max_ended_at = kwargs.get('max_ended_at')
    script = kwargs.get('script')
    allow_started_at_none = kwargs.get('allow_started_at_none', True)
    generate_script = kwargs.get('generate_script', True)
    generate_traces = kwargs.get('generate_traces', True)

    if run_no is not None:
        assert run.run_no == run_no
    else:
        assert sc(min_run_no) <= run.run_no <= sc(max_run_no)

    if not allow_started_at_none:
        assert run.started_at is not None

    assert sc(min_started_at) <= sc(run.started_at) <= sc(max_started_at)
    assert sc(min_ended_at) <= sc(run.ended_at) <= sc(max_ended_at)
    assert sc(run.started_at) <= sc(run.ended_at)

    if not run.started_at:
        assert not run.ended_at

    if script is not None:
        assert run.script == script
    elif not generate_script:
        assert not run.script

    traces = run.traces
    trace_calls = run.trace_calls
    prompts = run.prompts
    stdouts = run.stdouts
    if generate_traces:
        assert traces
        assert trace_calls
        assert prompts
        assert stdouts
    else:
        assert not traces
        assert not trace_calls
        assert not prompts
        assert not stdouts


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_run())
async def test_db(instance: Model) -> None:
    await assert_model_persistence([instance])
