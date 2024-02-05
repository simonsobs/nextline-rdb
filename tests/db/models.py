from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from nextline_rdb.models import ReprMixin


class Model(ReprMixin, DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class Foo(Model):
    __tablename__ = 'foo'
    bars: Mapped[list['Bar']] = relationship(back_populates='foo')


class Bar(Model):
    __tablename__ = 'bar'
    foo_id: Mapped[int] = mapped_column(ForeignKey('foo.id'))
    foo: Mapped[Foo] = relationship(back_populates='bars')


def register_session_events(session: sessionmaker[Session]) -> None:
    new: set[Model]

    @event.listens_for(session, 'before_flush')
    def _before_flush(session: Session, flush_context, instances):
        nonlocal new
        new = set(session.new)

    @event.listens_for(session, 'after_flush_postexec')
    def _after_flush_postexec(session: Session, flush_context):
        pass
