import datetime as dt

from hypothesis import strategies as st


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
