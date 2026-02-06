from typing import Annotated

from fastapi import Depends, HTTPException, status
from zion.auth.conf import settings
from zion.auth.deps.services import (
    AuthTokenServiceDep,
    AuthValidationServiceDep,
    UserServiceDep,
)
from zion.auth.enums import TokenType
from zion.auth.models import User
from zion.logger import get_logger

logger = get_logger(__name__)

TokenDep = Annotated[str, Depends(settings.AUTH_OAUTH2_SCHEME)]


async def get_current_user(
    token: TokenDep,
    token_service: AuthTokenServiceDep,
    user_service: UserServiceDep,
    auth_validation_service: AuthValidationServiceDep,
) -> User:
    token_data = token_service.verify(token, TokenType.ACCESS)

    if token_data is None:
        await logger.awarning("Could not verify access token", token=token)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = await user_service.get_by_credential(token_data.credential)

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    try:
        is_user_valid = await auth_validation_service.is_user_valid(user)
    except Exception as error:
        await logger.awarning("Error on user validaros %s", error)
        is_user_valid = False

    if not is_user_valid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
