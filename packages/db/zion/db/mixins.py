import datetime as dt

from nanoid import generate
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class IdMixin(MappedAsDataclass):
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        init=False,
    )


class PidMixin(MappedAsDataclass):
    """Public ID field

    The incremental integer primary keys might cause security vulnerabilities
    since they are easily guessable.
    """

    pid: Mapped[str] = mapped_column(
        String,
        default_factory=lambda: generate(),
        unique=True,
        init=False,
    )


class TimestampMixin(MappedAsDataclass):
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


class SoftDeleteMixin(MappedAsDataclass):
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

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = dt.datetime.now(dt.UTC)
