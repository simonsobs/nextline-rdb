from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_run import Run
    from .model_trace import Trace


class Stdout(Model):
    __tablename__ = "stdout"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str | None]
    written_at: Mapped[datetime | None]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped['Run'] = relationship(back_populates='stdouts')

    # TODO: Allow trace to be None. Stdout written from threads or async tasks
    # that are not traced should still be recorded.
    trace_id: Mapped[int] = mapped_column(ForeignKey('trace.id'))
    trace: Mapped['Trace'] = relationship(back_populates='stdouts')
