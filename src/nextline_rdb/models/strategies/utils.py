import datetime as dt

from hypothesis import strategies as st

SQLITE_INT_MIN = -9_223_372_036_854_775_808
SQLITE_INT_MAX = 9_223_372_036_854_775_807


def st_datetimes(
    min_value: dt.datetime = dt.datetime.min,
    max_value: dt.datetime = dt.datetime.max,
) -> st.SearchStrategy[dt.datetime]:
    '''A strategy for naive `datetime` objects without imaginary datetimes or folds.

    Note: timezones and folds are not supported by SQLite.
    '''
    return st.datetimes(
        min_value=min_value,
        max_value=max_value,
        allow_imaginary=False,
    ).filter(lambda dt_: dt_.fold == 0)
