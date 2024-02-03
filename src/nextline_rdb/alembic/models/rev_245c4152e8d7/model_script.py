from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_run import Run


class Script(Model):
    __tablename__ = 'script'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    current: Mapped[bool] = mapped_column(default=False)
    script: Mapped[str] = mapped_column(Text)

    runs: Mapped[list['Run']] = relationship(back_populates='script')

    _current: Mapped['CurrentScript'] = relationship(
        'CurrentScript', back_populates='script', cascade='all, delete-orphan'
    )


class CurrentScript(Model):
    '''The table that keeps track of the current script.

    This table is a singleton, i.e., it can have at most one row. This is
    enforced by a check constraint ensuring the 'id' is always 1.

    '''

    __tablename__ = 'current_script'
    id: Mapped[int] = mapped_column(primary_key=True, index=True, default=1)
    script_id: Mapped[int] = mapped_column(ForeignKey('script.id'))
    script: Mapped[Script] = relationship('Script', back_populates='_current')

    __table_args__ = (CheckConstraint('id = 1'),)
