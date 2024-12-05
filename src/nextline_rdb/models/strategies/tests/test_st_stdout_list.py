from typing import Optional, TypedDict

from hypothesis import Phase, given, note, settings
from hypothesis import strategies as st

from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_none_or, st_ranges

from ... import Model, Run
from .. import st_model_run, st_model_stdout_list, st_model_trace_list
from .funcs import assert_model_persistence


class StModelStdoutListKwargs(TypedDict, total=False):
    run: Optional[Run]
    min_size: int
    max_size: Optional[int]


@st.composite
def st_st_model_stdout_list_kwargs(draw: st.DrawFn) -> StModelStdoutListKwargs:
    kwargs = StModelStdoutListKwargs()

    if draw(st.booleans()):
        # generate_traces=False because that would generate stdout with traces
        run = draw(st_none_or(st_model_run(generate_traces=False)))
        kwargs['run'] = run
        if run:
            draw(st_none_or(st_model_trace_list(run=run, min_size=0, max_size=3)))

    if draw(st.booleans()):
        min_size, max_size = draw(
            st_ranges(
                st.integers,
                min_start=0,
                max_end=5,
                allow_start_none=False,
                allow_end_none=False,
            )
        )
        assert isinstance(min_size, int)
        kwargs['min_size'] = min_size
        kwargs['max_size'] = max_size

    return kwargs


@given(kwargs=st_st_model_stdout_list_kwargs())
def test_st_model_stdout_list_kwargs(kwargs: StModelStdoutListKwargs) -> None:
    assert sc(kwargs.get('min_size')) <= sc(kwargs.get('max_size'))


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_stdout_list_kwargs())
    note(kwargs)

    # Call the strategy to be tested
    stdouts = data.draw(st_model_stdout_list(**kwargs))

    # Assert the generated values
    run = kwargs.get('run')
    min_size = kwargs.get('min_size', 0)
    max_size = kwargs.get('max_size')

    if run and not run.traces:
        # `stdout` is not generated if `run` with no `traces` is provided
        assert not stdouts
    else:
        assert min_size <= len(stdouts) <= sc(max_size)

    if stdouts:
        runs = set(stdout.trace.run for stdout in stdouts)
        assert len(runs) == 1
        assert run is None or run is runs.pop()


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instances=st_model_stdout_list(max_size=5))
async def test_db(instances: list[Model]) -> None:
    await assert_model_persistence(instances)
