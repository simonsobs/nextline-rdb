def ensure_async_url(url: str) -> str:
    '''Convert an SQLAlchemy URL to an async one if necessary.

    Support only SQLite for now.

    >>> ensure_async_url('sqlite://')
    'sqlite+aiosqlite://'

    >>> ensure_async_url('sqlite+aiosqlite://')
    'sqlite+aiosqlite://'

    >>> ensure_async_url('sqlite:///foo.db')
    'sqlite+aiosqlite:///foo.db'

    >>> ensure_async_url('sqlite+aiosqlite:///foo.db')
    'sqlite+aiosqlite:///foo.db'

    >>> ensure_async_url('postgresql://scott:tiger@localhost/database')
    'postgresql://scott:tiger@localhost/database'

    '''
    scheme, rest = url.split("://", 1)
    if 'sqlite' not in scheme:
        return url
    if 'aiosqlite' in scheme:
        return url
    scheme = scheme.replace('sqlite', 'sqlite+aiosqlite')
    return f'{scheme}://{rest}'


def ensure_sync_url(url: str) -> str:
    '''Convert an SQLAlchemy URL to a sync one if necessary.

    Support only SQLite for now.

    >>> ensure_sync_url('sqlite://')
    'sqlite://'

    >>> ensure_sync_url('sqlite+aiosqlite://')
    'sqlite://'

    >>> ensure_sync_url('sqlite:///foo.db')
    'sqlite:///foo.db'

    >>> ensure_sync_url('sqlite+aiosqlite:///foo.db')
    'sqlite:///foo.db'

    >>> ensure_sync_url('postgresql+asyncpg://scott:tiger@localhost/database')
    'postgresql+asyncpg://scott:tiger@localhost/database'

    '''
    scheme, rest = url.split("://", 1)
    if 'sqlite' not in scheme:
        return url
    if 'aiosqlite' not in scheme:
        return url
    scheme = scheme.replace('sqlite+aiosqlite', 'sqlite')
    return f'{scheme}://{rest}'
