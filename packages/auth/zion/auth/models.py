import datetime as dt

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuthDbModel(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), index=True)
    email: Mapped[str] = mapped_column(String(50), index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default_factory=lambda: dt.datetime.now(dt.UTC)
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=dt.datetime.now(dt.UTC),
        default_factory=lambda: dt.datetime.now(dt.UTC),
    )

    deleted_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
