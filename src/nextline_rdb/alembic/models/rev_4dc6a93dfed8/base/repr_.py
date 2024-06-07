import enum
import math
from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import ColumnProperty, class_mapper


class ReprMixin:
    '''A mixin for ORM models with __repr__ for object reconstruction.

    Override methods of this class if necessary.
    '''

    def __repr__(self) -> str:
        '''Return a string that can be used to reconstruct the object.'''
        class_name = self._repr_class_name()
        init_args = self._repr_init_args()
        return f'{class_name}({init_args})'

    def _repr_class_name(self) -> str:
        '''The class name to use in the repr.'''
        return self.__class__.__qualname__

    def _repr_init_args(self) -> str:
        '''The arguments to use in the repr.'''
        keys = self._repr_keys()
        fmts = (f'{k}={self._repr_val(k)}' for k in keys)
        return ', '.join(fmts)

    def _repr_keys(self) -> Iterable[str]:
        '''The attribute names to include in the repr.'''
        props = class_mapper(self.__class__).iterate_properties
        columns = (p for p in props if isinstance(p, ColumnProperty))
        return (c.key for c in columns if self._repr_filter(c.key))

    def _repr_filter(self, key: str) -> bool:
        '''Exclude if the value is None.'''
        val = getattr(self, key)
        return val is not None

    def _repr_val(self, key: str) -> str:
        '''Format the value so it can be reconstructed.'''
        val = getattr(self, key)
        return repr_val(val)


def repr_val(val: Any) -> str:
    match val:
        case enum.Enum():
            return str(val)
        case int():
            return f'{val:_}'
        case math.inf:
            return 'float("inf")'
        case float(neg_inf) if neg_inf == float('-inf'):
            return 'float("-inf")'
        case float(nan_val) if math.isnan(nan_val):
            return 'float("nan")'
        case _:
            return repr(val)
