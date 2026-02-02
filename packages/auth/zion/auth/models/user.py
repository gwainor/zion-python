from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from zion.db import DbBaseModel
from zion.db.mixins import IdMixin, SoftDeleteMixin, TimestampMixin


class User(DbBaseModel, IdMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    username: Mapped[str | None] = mapped_column(String(20), default=None, index=True)
    email: Mapped[str | None] = mapped_column(String(50), default=None, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
