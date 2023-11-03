from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils import safe_compare
from nextline_rdb.utils.strategies import st_ranges


@given(st.data())
def test_allow_equal(data: st.DataObject) -> None:
    none_or_small, none_or_large = data.draw(
        st_ranges(st_=st.integers(), allow_equal=True)
    )
    assert safe_compare(none_or_small) <= safe_compare(none_or_large)
    assert safe_compare(none_or_large) >= safe_compare(none_or_small)


@given(st.data())
def test_not_allow_equal(data: st.DataObject) -> None:
    none_or_small, none_or_large = data.draw(
        st_ranges(st_=st.integers(), allow_equal=False)
    )
    assert safe_compare(none_or_small) < safe_compare(none_or_large)
    assert safe_compare(none_or_large) > safe_compare(none_or_small)
