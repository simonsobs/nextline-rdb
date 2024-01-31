from collections.abc import Iterable, Iterator
from typing import Tuple, TypeVar

_T = TypeVar('_T')


def mark_last(it: Iterable[_T]) -> Iterator[Tuple[bool, _T]]:
    '''Indicate the end of the iteration.

    >>> list(mark_last([1, 2, 3]))
    [(False, 1), (False, 2), (True, 3)]

    >>> list(mark_last([1]))
    [(True, 1)]

    >>> list(mark_last([]))
    []


    This function is copied from `c5backup`:
    https://github.com/simonsobs/c5backup/blob/v0.3.0/src/c5backup/util/gen.py

    '''
    first = True
    for i in it:
        if first:
            first = False
            p = i
            continue
        yield False, p
        p = i
    else:
        if not first:
            yield True, p
