from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_prompt import Prompt
    from .model_script import Script
    from .model_stdout import Stdout
    from .model_trace import Trace


class Run(Model):
    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_no: Mapped[int] = mapped_column(unique=True)
    state: Mapped[str | None]
    started_at: Mapped[datetime | None]
    ended_at: Mapped[datetime | None]
    script_old: Mapped[str | None] = mapped_column(Text)
    exception: Mapped[str | None] = mapped_column(Text)

    script_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('script.id'), nullable=True
    )
    script: Mapped[Optional['Script']] = relationship(back_populates='runs')

    traces: Mapped[list["Trace"]] = relationship(back_populates="run")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="run")
    stdouts: Mapped[list["Stdout"]] = relationship(back_populates="run")
