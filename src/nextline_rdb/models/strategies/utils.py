import datetime as dt
from typing import Optional

from nextline_rdb.utils.strategies import st_datetimes, st_ranges


def st_started_at_ended_at(
    min_start: Optional[dt.datetime] = None,
    max_start: Optional[dt.datetime] = None,
    min_end: Optional[dt.datetime] = None,
    max_end: Optional[dt.datetime] = None,
) -> tuple[None, None] | tuple[dt.datetime, Optional[dt.datetime]]:
    '''
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
