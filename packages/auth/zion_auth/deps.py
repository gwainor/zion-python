from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from zion_auth.models import User
from zion_auth.protocols import (
    DatabaseAdapterProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    ValidationServiceProtocol,
    ZionAuthServiceProtocol,
)
from zion_auth.settings import settings
from zion_auth.utils import import_dependency


DatabaseAdapterDep = Annotated[
    DatabaseAdapterProtocol,
    Depends(import_dependency("database_adapter")),
]

PasswordServiceDep = Annotated[
    PasswordServiceProtocol,
    Depends(import_dependency("password_service")),
]

TokenServiceDep = Annotated[
    TokenServiceProtocol,
    Depends(import_dependency("token_service")),
]

ValidationServiceDep = Annotated[
    ValidationServiceProtocol,
    Depends(import_dependency("validation_service")),
]

ZionAuthDep = Annotated[
    ZionAuthServiceProtocol,
    Depends(import_dependency("service")),
]

TokenDep = Annotated[
    str,
    Depends(OAuth2PasswordBearer(tokenUrl=settings.oauth2_scheme_token_url)),
]


async def get_current_user(zion_auth: ZionAuthDep, token: TokenDep) -> User:
    return await zion_auth.get_current_user(token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
