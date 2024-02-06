from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_run import Run


class Script(Model):
    __tablename__ = 'script'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    script: Mapped[str] = mapped_column(Text)

    runs: Mapped[list['Run']] = relationship(back_populates='script')

    _current: Mapped[Optional['CurrentScript']] = relationship(
        'CurrentScript', back_populates='script', cascade='all, delete-orphan'
    )

    @property
    def current(self) -> bool:
        '''True if this script is the current script.

        At most one script can be the current script at any time.
        '''
        return self._current is not None

    @current.setter
    def current(self, value: bool):
        if value and self._current is None:
            self._current = CurrentScript(script=self)
        elif not value:
            self._current = None


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
