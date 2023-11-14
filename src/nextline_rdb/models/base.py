import enum
import math
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import ColumnProperty, DeclarativeBase, class_mapper

# Constraints naming conventions
#
# SQLAlchemy 2 Doc:
# https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions
#
# About the change on "ck":
# https://stackoverflow.com/a/56000475/7309855
#
# Equivalent code in ProductDB:
# https://github.com/simonsobs/acondbs/blob/7b4e5ab967ce/acondbs/db/sa.py
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


class Model(DeclarativeBase):
    metadata = metadata

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
