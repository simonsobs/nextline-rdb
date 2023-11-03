from collections.abc import Iterable
from typing import Optional, TypeVar

T = TypeVar('T')


def safe_min(vals: Iterable[T], default: Optional[T] = None) -> Optional[T]:
    '''The smallest item in `vals` that is not `None`.
    
    >>> safe_min([None, 1, 2, None])
    1
    
    It returns `None` if `vals` is empty or all items in `vals` are `None`.
    >>> print(safe_min([None, None]))
    None

    >>> print(safe_min([]))
    None

    If `default` is given, it returns `default` instead of `None`.
    >>> safe_min([None, None], default=-1)
    -1
    
    >>> safe_min([], default=-1)
    -1
    '''
    return min((v for v in vals if v is not None), default=default)


def safe_max(vals: Iterable[T], default: Optional[T] = None) -> Optional[T]:
    '''The largest item in `vals` that is not `None`.
    
    >>> safe_max([None, 1, 2, None])
    2

    It returns `None` if `vals` is empty or all items in `vals` are `None`.
    >>> print(safe_max([None, None]))
    None

    >>> print(safe_max([]))
    None

    If `default` is given, it returns `default` instead of `None`.
    >>> safe_max([None, None], default=-1)
    -1

    >>> safe_max([], default=-1)
    -1
    '''
    return max((v for v in vals if v is not None), default=default)
