from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from .convention import NAMING_CONVENTION
from .repr_ import ReprMixin

metadata = MetaData(naming_convention=dict(NAMING_CONVENTION))


class Model(ReprMixin, DeclarativeBase):
    metadata = metadata
