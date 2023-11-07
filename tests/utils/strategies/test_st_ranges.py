from typing import Optional, TypeVar

from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils import safe_compare
from nextline_rdb.utils.strategies import (
    st_datetimes,
    st_none_or,
    st_ranges,
    st_sqlite_ints,
)

T = TypeVar('T')


@st.composite
def st_min_max_start(
    draw: st.DrawFn,
    st_: st.SearchStrategy[T],
) -> tuple[Optional[T], Optional[T]]:
    min_ = draw(st_none_or(st_), label='min')
    st_max = st_.filter(lambda x: x >= min_) if min_ is not None else st_  # type: ignore
    max_ = draw(st_none_or(st_max), label='max')
    return min_, max_


@st.composite
def st_min_max_end(
    draw: st.DrawFn,
    st_: st.SearchStrategy[T],
    min_start: Optional[T] = None,
) -> tuple[Optional[T], Optional[T]]:
    st_min = st_.filter(lambda x: x >= min_start) if min_start is not None else st_  # type: ignore
    min_ = draw(st_none_or(st_min), label='min')
    min_value = min_ if min_ is not None else min_start
    st_max = st_.filter(lambda x: x >= min_value) if min_value is not None else st_  # type: ignore
    max_ = draw(st_none_or(st_max), label='max')
    return min_, max_


@given(st.data())
def test_st_ranges(data: st.DataObject) -> None:
    st_ = data.draw(st.sampled_from([st_sqlite_ints(), st_datetimes()]))

    min_start, max_start = data.draw(st_min_max_start(st_=st_))
    min_end, max_end = data.draw(st_min_max_end(st_=st_, min_start=min_start))
    allow_start_none = data.draw(st.booleans())
    allow_end_none = data.draw(st.booleans())
    allow_equal = data.draw(st.booleans())
    let_end_none_if_start_none = data.draw(st.booleans())

    start, end = data.draw(
        st_ranges(
            st_=st_,
            min_start=min_start,
            max_start=max_start,
            min_end=min_end,
            max_end=max_end,
            allow_start_none=allow_start_none,
            allow_end_none=allow_end_none,
            allow_equal=allow_equal,
            let_end_none_if_start_none=let_end_none_if_start_none,
        )
    )

    if not allow_start_none:
        assert start is not None

    if start is None and let_end_none_if_start_none:
        assert end is None
    elif not allow_end_none:
        assert end is not None

    if allow_equal:
        assert safe_compare(start) <= safe_compare(end)
    else:
        assert safe_compare(start) < safe_compare(end)

    assert safe_compare(min_start) <= safe_compare(start) <= safe_compare(max_start)
    assert safe_compare(min_end) <= safe_compare(end) <= safe_compare(max_end)
