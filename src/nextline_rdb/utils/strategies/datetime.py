import datetime as dt
from typing import Optional

from hypothesis import strategies as st

from .misc import st_ranges


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


def st_datetime_ranges(
    min_start: Optional[dt.datetime] = None,
    max_start: Optional[dt.datetime] = None,
    min_end: Optional[dt.datetime] = None,
    max_end: Optional[dt.datetime] = None,
) -> tuple[None, None] | tuple[dt.datetime, Optional[dt.datetime]]:
    '''
    >>> st_datetime_ranges().example()
    (...)
    '''
    return st_ranges(
        st_=st_datetimes(),
        min_start=min_start,
        max_start=max_start,
        min_end=min_end,
        max_end=max_end,
        allow_start_none=True,
        allow_end_none=True,
        allow_equal=True,
    ).filter(lambda x: not (x[0] is None and x[1] is not None))
