from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils import mark_last


@given(st.lists(st.integers()))
def test_one(items: list[int]):
    it = iter(items)
    actual = list(mark_last(it))

    expected = [(i == len(items) - 1, e) for i, e in enumerate(items)]

    assert actual == expected
