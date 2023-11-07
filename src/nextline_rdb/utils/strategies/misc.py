from typing import Optional, TypeVar

from hypothesis import strategies as st

from nextline_rdb.utils import safe_max, safe_min

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


def st_in_range(
    st_: st.SearchStrategy[T],
    min_value: Optional[T] = None,
    max_value: Optional[T] = None,
):
    if min_value is not None:
        st_ = st_.filter(lambda x: x >= min_value)  # type: ignore
    if max_value is not None:
        st_ = st_.filter(lambda x: x <= max_value)  # type: ignore
    return st_


def st_ranges(
    st_: st.SearchStrategy[T],
    min_start: Optional[T] = None,
    max_start: Optional[T] = None,
    min_end: Optional[T] = None,
    max_end: Optional[T] = None,
    allow_start_none: bool = True,
    allow_end_none: bool = True,
    let_end_none_if_start_none: bool = False,
    allow_equal: bool = True,
) -> st.SearchStrategy[tuple[Optional[T], Optional[T]]]:
    '''Generate two values (start, end) from a strategy, where start <= end.

    The minimum and maximum values can be specified by `min_start`,
    `max_start`, `min_end`, `max_end`.

    `start` (`end`) can be `None` if `allow_start_none` (`allow_end_none`) is `True`.

    If `let_end_none_if_start_none` is `True`, `end` will be always `None` when
    `start` is `None` regardless of `allow_end_none`.

    If `allow_equal` is `False`, `start` and `end` cannot be equal, i.e., `start < end`.

    >>> start, end = st_ranges(
    ...     st.integers(),
    ...     min_start=0,
    ...     max_end=10,
    ...     allow_start_none=False,
    ...     allow_end_none=False,
    ... ).example()

    The results can be, for example, used as min_value and max_value of st.integers().

    >>> i = st.integers(min_value=start, max_value=end).example()
    >>> start <= i <= end
    True

    The results can also be used as min_size and max_size of st.lists().

    >>> l = st.lists(st.integers(), min_size=start, max_size=end).example()
    >>> start <= len(l) <= end
    True

    '''

    def st_start():
        _max_start = safe_min((max_start, max_end))
        _st = st_in_range(st_, min_start, _max_start)
        return st_none_or(_st) if allow_start_none else _st

    def st_end(start: T | None):
        _min_end = safe_max((min_start, start, min_end))
        if min_end is not None and max_end is not None:
            assert min_end <= max_end  # type: ignore
        if start is None and let_end_none_if_start_none:
            return st.none()
        _st = st_in_range(st_, _min_end, max_end)
        if start is not None and not allow_equal:
            _st = _st.filter(lambda x: x > start)
        return st_none_or(_st) if allow_end_none else _st

    return st_start().flatmap(
        lambda start: st.tuples(st.just(start), st_end(start=start))
    )
