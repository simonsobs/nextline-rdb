from collections.abc import Iterable
from typing import Optional, TypeVar

T = TypeVar('T')


def safe_min(vals: Iterable[T], default: Optional[T] = None) -> Optional[T]:
    return min((v for v in vals if v is not None), default=default)


def safe_max(vals: Iterable[T], default: Optional[T] = None) -> Optional[T]:
    return max((v for v in vals if v is not None), default=default)
