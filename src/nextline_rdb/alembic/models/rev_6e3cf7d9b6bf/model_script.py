from typing import TYPE_CHECKING

from sqlalchemy import Text
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
