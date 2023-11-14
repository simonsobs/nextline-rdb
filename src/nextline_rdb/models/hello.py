from sqlalchemy.orm import Mapped, mapped_column

from .base import Model


class Hello(Model):
    __tablename__ = "hello"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message: Mapped[str | None]
