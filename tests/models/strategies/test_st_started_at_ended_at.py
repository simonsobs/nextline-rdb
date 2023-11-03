from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.models.strategies import st_started_at_ended_at
from nextline_rdb.utils.strategies import st_datetimes, st_ranges


@given(st.data())
def test_st_started_at_ended_at(data: st.DataObject) -> None:
    min_start, max_start = data.draw(st_ranges(st_=st_datetimes()))
    min_end, max_end = data.draw(st_ranges(st_=st_datetimes(), min_start=min_start))

    start, end = data.draw(
        st_started_at_ended_at(
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
