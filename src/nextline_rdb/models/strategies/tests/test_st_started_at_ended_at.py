import datetime as dt
from typing import Optional, TypedDict

from hypothesis import given
from hypothesis import strategies as st

from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_datetimes, st_ranges

from .. import st_started_at_ended_at


class StStartedAtEndedAtKwargs(TypedDict, total=False):
    min_start: Optional[dt.datetime]
    max_start: Optional[dt.datetime]
    min_end: Optional[dt.datetime]
    max_end: Optional[dt.datetime]
    allow_start_none: bool
    allow_end_none: bool
    allow_equal: bool


@st.composite
def st_st_started_at_ended_at_kwargs(draw: st.DrawFn) -> StStartedAtEndedAtKwargs:
    kwargs = StStartedAtEndedAtKwargs()

    min_start: Optional[dt.datetime] = None
    if draw(st.booleans()):
        min_start, max_start = draw(st_ranges(st_datetimes))
        kwargs['min_start'] = min_start
        kwargs['max_start'] = max_start

    if draw(st.booleans()):
        min_end, max_end = draw(st_ranges(st_datetimes, min_start=min_start))
        kwargs['min_end'] = min_end
        kwargs['max_end'] = max_end

    if draw(st.booleans()):
        kwargs['allow_start_none'] = draw(st.booleans())

    if draw(st.booleans()):
        kwargs['allow_end_none'] = draw(st.booleans())

    if draw(st.booleans()):
        kwargs['allow_equal'] = draw(st.booleans())

    return kwargs


@given(kwargs=st_st_started_at_ended_at_kwargs())
def test_st_started_at_ended_at_kwargs(kwargs: StStartedAtEndedAtKwargs) -> None:
    assert sc(kwargs.get('min_start')) <= sc(kwargs.get('max_start'))
    assert sc(kwargs.get('min_start')) <= sc(kwargs.get('min_end'))
    assert sc(kwargs.get('min_end')) <= sc(kwargs.get('max_end'))


@given(data=st.data())
def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_started_at_ended_at_kwargs())

    # Call the strategy to be tested
    start, end = data.draw(st_started_at_ended_at(**kwargs))

    # Assert the generated values
    min_start = kwargs.get('min_start')
    max_start = kwargs.get('max_start')
    min_end = kwargs.get('min_end')
    max_end = kwargs.get('max_end')
    allow_start_none = kwargs.get('allow_start_none', True)
    allow_end_none = kwargs.get('allow_end_none', True)
    allow_equal = kwargs.get('allow_equal', True)

    if not start:
        assert not end

    if not allow_start_none:
        assert start is not None

    if start is not None and not allow_end_none:
        assert end is not None

    if allow_equal:
        assert sc(start) <= sc(end)
    else:
        assert sc(start) < sc(end)

    assert sc(min_start) <= sc(start) <= sc(max_start)
    assert sc(min_end) <= sc(end) <= sc(max_end)
