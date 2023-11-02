import datetime as dt
from typing import Optional

from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils.strategies import st_datetime_ranges, st_datetimes, st_none_or


@st.composite
def st_min_max_start(
    draw: st.DrawFn,
) -> tuple[Optional[dt.datetime], Optional[dt.datetime]]:
    min_ = draw(st_none_or(st_datetimes()), label='min')
    max_ = draw(st_none_or(st_datetimes(min_value=min_)), label='max')
    return min_, max_


@st.composite
def st_min_max_end(
    draw: st.DrawFn,
    min_start: Optional[dt.datetime] = None,
) -> tuple[Optional[dt.datetime], Optional[dt.datetime]]:
    min_ = draw(st_none_or(st_datetimes(min_value=min_start)), label='min')
    max_ = draw(st_none_or(st_datetimes(min_value=min_ or min_start)), label='max')
    return min_, max_


@given(st.data())
def test_st_datetime_range(data: st.DataObject) -> None:
    min_start, max_start = data.draw(st_min_max_start(), label='start')
    min_end, max_end = data.draw(st_min_max_end(min_start=min_start), label='end')

    start, end = data.draw(
        st_datetime_ranges(
            min_start=min_start,
            max_start=max_start,
            min_end=min_end,
            max_end=max_end,
        )
    )

    if not start:
        assert not end

    if start and end:
        assert start <= end

    if start:
        if min_start:
            assert min_start <= start
        if max_start:
            assert start <= max_start

    if end:
        if min_end:
            assert min_end <= end
        if max_end:
            assert end <= max_end
