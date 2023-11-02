from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils.strategies import st_min_max_tuples


@given(st.data())
def test_one(data: st.DataObject):
    min_max, max_max = data.draw(st_min_max_tuples())
    min_min, max_min = data.draw(st_min_max_tuples(max_max=max_max))

    min_, max_ = data.draw(
        st_min_max_tuples(
            min_min=min_min,
            max_min=max_min,
            min_max=min_max,
            max_max=max_max,
        )
    )

    assert min_min <= min_
    if max_min is not None:
        assert min_ <= max_min

    if max_ is not None:
        assert min_ <= max_
        assert min_max <= max_
        if max_max is not None:
            assert max_ <= max_max
