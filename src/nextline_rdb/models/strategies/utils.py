import datetime as dt
from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.utils.strategies import st_datetimes, st_ranges


def st_started_at_ended_at(
    min_start: Optional[dt.datetime] = None,
    max_start: Optional[dt.datetime] = None,
    min_end: Optional[dt.datetime] = None,
    max_end: Optional[dt.datetime] = None,
) -> st.SearchStrategy[tuple[None, None] | tuple[dt.datetime, Optional[dt.datetime]]]:
    '''Generate two naive datetime objects: started_at and ended_at.

    `started_at` and `ended_at` can be `None`. If `started_at` is `None`,
    `ended_at` is always `None`.

    When neither of them is `None`, `started_at` is earlier than or the same
    time as `ended_at`.

    >>> st_started_at_ended_at().example()
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
