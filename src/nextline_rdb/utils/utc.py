from datetime import datetime, timezone


def utc_timestamp(naive: datetime) -> int:
    '''Return the timestamp of the naive datetime object as UTC.

    https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp

    >>> utc_timestamp(datetime(2022, 10, 30, 17, 13, 20))
    1667150000

    '''
    assert not is_timezone_aware(naive)
    aware = naive.replace(tzinfo=timezone.utc)
    return int(aware.timestamp())


def is_timezone_aware(dt: datetime) -> bool:
    '''Return True if the datetime object has a timezone.

    https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive

    >>> is_timezone_aware(datetime(2022, 10, 30, 17, 13, 20))
    False

    >>> is_timezone_aware(datetime(2022, 10, 30, 17, 13, 20, tzinfo=timezone.utc))
    True

    '''
    return (dt.tzinfo and dt.tzinfo.utcoffset(dt)) is not None


def to_naive_utc(dt: datetime) -> datetime:
    '''Convert a datetime to a naive UTC datetime.

    >>> to_naive_utc(datetime(2022, 10, 30, 17, 13, 20, tzinfo=timezone.utc))
    datetime.datetime(2022, 10, 30, 17, 13, 20)

    >>> to_naive_utc(datetime(2022, 10, 30, 17, 13, 20))
    datetime.datetime(2022, 10, 30, 17, 13, 20)

    >>> from datetime import timedelta, timezone
    >>> est = timezone(timedelta(hours=-5))
    >>> to_naive_utc(datetime(2022, 10, 30, 12, 13, 20, tzinfo=est))
    datetime.datetime(2022, 10, 30, 17, 13, 20)

    '''
    if is_timezone_aware(dt):
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
