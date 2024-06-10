from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_run import Run
    from .model_trace import Trace
    from .model_trace_call import TraceCall


class Prompt(Model):
    __tablename__ = "prompt"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prompt_no: Mapped[int]  # unique in each run
    open: Mapped[bool]
    started_at: Mapped[datetime]
    stdout: Mapped[str | None]
    command: Mapped[str | None]
    ended_at: Mapped[datetime | None]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped['Run'] = relationship(back_populates='prompts')

    trace_id: Mapped[int] = mapped_column(ForeignKey('trace.id'))
    trace: Mapped['Trace'] = relationship(back_populates='prompts')

    trace_call_id: Mapped[int] = mapped_column(ForeignKey('trace_call.id'))
    trace_call: Mapped['TraceCall'] = relationship(back_populates='prompts')

    __table_args__ = (UniqueConstraint("run_id", "prompt_no"),)
