import enum
import math
from typing import Any

from sqlalchemy.orm import ColumnProperty, class_mapper


class ReprMixin:
    def __repr__(self) -> str:
        '''Return a string that can be used to reconstruct the object.'''
        props = class_mapper(self.__class__).iterate_properties
        columns = (p for p in props if isinstance(p, ColumnProperty))
        keys = (c.key for c in columns if self._repr_filter(c.key))
        fmts = (f'{k}={self._repr_val(k)}' for k in keys)
        return f'{self.__class__.__qualname__}({", ".join(fmts)})'

    def _repr_filter(self, key: str) -> bool:
        '''Exclude if the value is None. Override this method if necessary.'''
        val = getattr(self, key)
        return val is not None

    def _repr_val(self, key: str) -> str:
        '''Format the value so it can be reconstructed. Override this method if necessary.'''
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
