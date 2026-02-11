import datetime as dt

from ulid import ULID
from zion_auth.settings import settings

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


# Default Base for users who don't provide their own
class DefaultBase(MappedAsDataclass, DeclarativeBase):
    pass


# Get the Base from settings or use default
def _get_base():
    if settings.sqlalchemy_base_import:
        return settings.sqlalchemy_base_import
    return DefaultBase


class UserSqlModel(_get_base()):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    pid: Mapped[str] = mapped_column(
        String(26),
        unique=True,
        index=True,
        init=False,
        default_factory=lambda: str(ULID()),
    )

    hashed_password: Mapped[str] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String(20), default=None, index=True)
    email: Mapped[str | None] = mapped_column(String(50), default=None, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Soft deletion
    deleted_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        init=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        init=False,
    )

    # Timestamps
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: dt.datetime.now(dt.UTC),
        init=False,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: dt.datetime.now(dt.UTC),
        onupdate=lambda: dt.datetime.now(dt.UTC),
        init=False,
    )
