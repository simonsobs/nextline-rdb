from typing import Optional, TypeVar

from hypothesis import strategies as st

SQLITE_INT_MIN = -9_223_372_036_854_775_808  # 2 ** 63 * -1
SQLITE_INT_MAX = 9_223_372_036_854_775_807  # 2 ** 63 - 1

T = TypeVar('T')


def st_none_or(st_: st.SearchStrategy[T]) -> st.SearchStrategy[Optional[T]]:
    '''A strategy for `None` or values from another strategy.

    >>> v = st_none_or(st.integers()).example()
    >>> v is None or isinstance(v, int)
    True
    '''
    return st.one_of(st.none(), st_)


def st_sqlite_ints(
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> st.SearchStrategy[int]:
    '''A strategy for integers within the range of SQLite's `INTEGER` type.

    >>> int_ = st_sqlite_ints().example()
    >>> int_ >= SQLITE_INT_MIN
    True

    >>> int_ <= SQLITE_INT_MAX
    True
    '''
    if min_value is None:
        min_value = SQLITE_INT_MIN
    else:
        min_value = max(min_value, SQLITE_INT_MIN)

    if max_value is None:
        max_value = SQLITE_INT_MAX
    else:
        max_value = min(max_value, SQLITE_INT_MAX)

    return st.integers(min_value=min_value, max_value=max_value)


@st.composite
def st_min_max_tuples(
    draw,
    min_min=0,
    max_min: Optional[int] = None,
    min_max=0,
    max_max: Optional[int] = None,
):
    '''Generate 2-tuples (min, max) in which min <= max or max is None.

    >>> min_, max_ = st_min_max_tuples(max_max=10).example()

    The results can be, for example, used as min_value and max_value of st.integers().

    >>> i = st.integers(min_value=min_, max_value=max_).example()
    >>> min_ <= i <= max_
    True

    The results can also be used to generate lists of a certain length.

    >>> l = st.lists(st.integers(), min_size=min_, max_size=max_).example()
    >>> min_ <= len(l) <= max_
    True
    '''

    if max_max is not None:
        if max_min is not None:
            assert max_min <= max_max
        else:
            max_min = max_max

    min_ = draw(st.integers(min_value=min_min, max_value=max_min))

    min_max = max(min_max, min_)

    if max_max is None:
        max_ = draw(st.one_of(st.none(), st.integers(min_value=min_max)))
    else:
        max_ = draw(st.integers(min_value=min_max, max_value=max_max))

    return min_, max_
