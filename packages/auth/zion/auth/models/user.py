from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from zion.db import DbBaseModel
from zion.db.mixins import IdMixin, PidMixin, SoftDeleteMixin, TimestampMixin


class User(DbBaseModel, IdMixin, TimestampMixin, SoftDeleteMixin, PidMixin):
    __tablename__ = "users"

    hashed_password: Mapped[str] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String(20), default=None, index=True)
    email: Mapped[str | None] = mapped_column(String(50), default=None, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
