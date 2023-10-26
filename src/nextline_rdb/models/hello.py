from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Hello(Base):
    __tablename__ = "hello"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message: Mapped[str | None]
