from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.models.strategies import st_started_at_ended_at
from nextline_rdb.utils import safe_compare as sc
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

    assert sc(start) <= sc(end)
    assert sc(min_start) <= sc(start) <= sc(max_start)
    assert sc(min_end) <= sc(end) <= sc(max_end)
