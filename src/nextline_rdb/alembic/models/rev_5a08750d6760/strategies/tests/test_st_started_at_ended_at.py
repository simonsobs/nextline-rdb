from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils import safe_compare as sc
from nextline_rdb.utils.strategies import st_datetimes, st_ranges

from .. import st_started_at_ended_at


@given(st.data())
def test_st_started_at_ended_at(data: st.DataObject) -> None:
    min_start, max_start = data.draw(st_ranges(st_=st_datetimes))
    min_end, max_end = data.draw(st_ranges(st_=st_datetimes, min_start=min_start))
    allow_start_none = data.draw(st.booleans())
    allow_end_none = data.draw(st.booleans())
    allow_equal = data.draw(st.booleans())

    start, end = data.draw(
        st_started_at_ended_at(
            min_start=min_start,
            max_start=max_start,
            min_end=min_end,
            max_end=max_end,
            allow_start_none=allow_start_none,
            allow_end_none=allow_end_none,
            allow_equal=allow_equal,
        )
    )

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
