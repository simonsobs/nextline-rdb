from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_prompt import Prompt
    from .model_run import Run
    from .model_trace import Trace


class TraceCall(Model):
    __tablename__ = 'trace_call'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trace_call_no: Mapped[int]  # unique in each run
    started_at: Mapped[datetime]
    file_name: Mapped[str | None]
    line_no: Mapped[int | None]
    event: Mapped[str]
    ended_at: Mapped[datetime | None]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped['Run'] = relationship(back_populates='trace_calls')

    trace_id: Mapped[int] = mapped_column(ForeignKey('trace.id'))
    trace: Mapped['Trace'] = relationship(back_populates='trace_calls')

    prompts: Mapped[list['Prompt']] = relationship(back_populates='trace_call')

    __table_args__ = (UniqueConstraint('run_id', 'trace_call_no'),)
