import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pid: str
    hashed_password: str
    username: str | None = None
    email: str | None = None
    is_active: bool = True
    is_email_verified: bool = False
    is_deleted: bool = False
    deleted_at: dt.datetime | None = None
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.UTC))
    updated_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.UTC))


class TokenData(BaseModel):
    public_id: str
