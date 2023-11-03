from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils import safe_compare
from nextline_rdb.utils.strategies import st_ranges


@given(st.data())
def test_allow_equal(data: st.DataObject) -> None:
    maybe_none, larger = data.draw(
        st_ranges(
            st_=st.integers(),
            allow_start_none=True,
            allow_end_none=False,
            allow_equal=True,
        )
    )
    assert larger is not None
    assert safe_compare(maybe_none) <= larger
    assert larger >= safe_compare(maybe_none)


@given(st.data())
def test_not_allow_equal(data: st.DataObject) -> None:
    maybe_none, larger = data.draw(
        st_ranges(
            st_=st.integers(),
            allow_start_none=True,
            allow_end_none=False,
            allow_equal=False,
        )
    )
    assert larger is not None
    assert safe_compare(maybe_none) < larger
    assert larger > safe_compare(maybe_none)
