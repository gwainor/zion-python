from fastapi.security import OAuth2PasswordBearer
from zion.config import AppConf, settings

from .enums import CredentialType


class Conf(AppConf):
    ALGORITHM: str = "HS256"
    LOGIN_WITH: list[CredentialType] = [CredentialType.EMAIL]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
    SERVICES: dict[str, str] = {
        "USER": "zion.auth.services.UserService",
        "TOKEN": "zion.auth.services.TokenService",
        "AUTH_VALIDATION": "zion.auth.services.AuthValidationService",
    }
    USER_VALIDATORS: list[str] = [
        "zion.auth.validators.user.is_deleted",
    ]

    class Meta:
        prefix = "auth"
        required = ["SECRET_KEY"]


__all__ = ["Conf", "settings"]
