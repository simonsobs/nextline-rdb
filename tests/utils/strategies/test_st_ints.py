from typing import TypeVar

from graphql import GRAPHQL_MAX_INT, GRAPHQL_MIN_INT
from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils import safe_compare
from nextline_rdb.utils.strategies import (
    SQLITE_INT_MAX,
    SQLITE_INT_MIN,
    st_graphql_ints,
    st_ranges,
    st_sqlite_ints,
)

T = TypeVar('T')


@given(st.data())
def test_st_sqlite_ints(data: st.DataObject) -> None:
    min_, max_ = data.draw(
        st_ranges(st_=st.integers, max_start=SQLITE_INT_MAX, min_end=SQLITE_INT_MIN)
    )

    i = data.draw(st_sqlite_ints(min_value=min_, max_value=max_))

    assert SQLITE_INT_MIN <= i <= SQLITE_INT_MAX
    assert safe_compare(min_) <= i <= safe_compare(max_)


@given(st.data())
def test_st_graphql_ints(data: st.DataObject) -> None:
    min_, max_ = data.draw(
        st_ranges(st_=st.integers, max_start=GRAPHQL_MAX_INT, min_end=GRAPHQL_MIN_INT)
    )

    i = data.draw(st_graphql_ints(min_value=min_, max_value=max_))

    assert GRAPHQL_MIN_INT <= i <= GRAPHQL_MAX_INT
    assert safe_compare(min_) <= i <= safe_compare(max_)
