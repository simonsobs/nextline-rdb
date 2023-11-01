import datetime as dt
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


def st_datetimes(
    min_value: Optional[dt.datetime] = None,
    max_value: Optional[dt.datetime] = None,
) -> st.SearchStrategy[dt.datetime]:
    '''A strategy for naive `datetime` objects without imaginary datetimes or folds.

    Note: timezones and folds are not supported by SQLite.

    >>> dt_ = st_datetimes().example()
    >>> dt_.tzinfo is None
    True

    >>> dt_.fold
    0
    '''
    if min_value is None:
        min_value = dt.datetime.min

    if max_value is None:
        max_value = dt.datetime.max

    return st.datetimes(
        min_value=min_value,
        max_value=max_value,
        allow_imaginary=False,
    ).filter(lambda dt_: dt_.fold == 0)
