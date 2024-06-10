from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_prompt import Prompt
    from .model_run import Run
    from .model_stdout import Stdout
    from .model_trace_call import TraceCall


class Trace(Model):
    __tablename__ = 'trace'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trace_no: Mapped[int]  # unique in each run
    state: Mapped[str]
    thread_no: Mapped[int]
    task_no: Mapped[int | None]
    started_at: Mapped[datetime]
    ended_at: Mapped[datetime | None]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped['Run'] = relationship(back_populates='traces')

    trace_calls: Mapped[list['TraceCall']] = relationship(
        back_populates='trace', cascade='all, delete-orphan'
    )
    prompts: Mapped[list['Prompt']] = relationship(
        back_populates='trace', cascade='all, delete-orphan'
    )
    stdouts: Mapped[list['Stdout']] = relationship(back_populates='trace')

    __table_args__ = (UniqueConstraint('run_id', 'trace_no'),)
