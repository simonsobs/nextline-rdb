from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model

if TYPE_CHECKING:
    from .model_prompt import Prompt
    from .model_stdout import Stdout
    from .model_trace import Trace


class Run(Model):
    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_no: Mapped[int] = mapped_column(unique=True)
    state: Mapped[str | None]
    started_at: Mapped[datetime | None]
    ended_at: Mapped[datetime | None]
    script: Mapped[str | None] = mapped_column(Text)
    exception: Mapped[str | None] = mapped_column(Text)

    traces: Mapped[list["Trace"]] = relationship(back_populates="run")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="run")
    stdouts: Mapped[list["Stdout"]] = relationship(back_populates="run")
