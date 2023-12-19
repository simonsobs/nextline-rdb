from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from nextline_rdb.models import ReprMixin


class Model(ReprMixin, DeclarativeBase):
    pass


class Foo(Model):
    __tablename__ = 'foo'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bars: Mapped[list['Bar']] = relationship(back_populates='foo')


class Bar(Model):
    __tablename__ = 'bar'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    foo_id: Mapped[int] = mapped_column(ForeignKey('foo.id'))
    foo: Mapped[Foo] = relationship(back_populates='bars')
