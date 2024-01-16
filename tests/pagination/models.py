from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from nextline_rdb.models import NAMING_CONVENTION, ReprMixin

metadata = MetaData(naming_convention=dict(NAMING_CONVENTION))


class Base(ReprMixin, DeclarativeBase):
    metadata = metadata


class Entity(Base):
    __tablename__ = 'entity'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    num: Mapped[int | None]
    txt: Mapped[str | None]
