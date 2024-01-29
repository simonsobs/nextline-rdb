from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_run import Run
    from .model_trace import Trace


class Prompt(Model):
    __tablename__ = "prompt"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_no: Mapped[int]
    trace_no: Mapped[int]
    prompt_no: Mapped[int]
    open: Mapped[bool]
    event: Mapped[str]
    started_at: Mapped[datetime]
    file_name: Mapped[str | None]
    line_no: Mapped[int | None]
    stdout: Mapped[str | None]
    command: Mapped[str | None]
    ended_at: Mapped[datetime | None]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped['Run'] = relationship(back_populates='prompts')

    trace_id: Mapped[int] = mapped_column(ForeignKey('trace.id'))
    trace: Mapped['Trace'] = relationship(back_populates='prompts')

    __table_args__ = (UniqueConstraint("run_no", "prompt_no"),)
