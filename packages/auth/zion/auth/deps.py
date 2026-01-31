from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from zion.auth.conf import settings
from zion.auth.enums import TokenType
from zion.auth.utils import tokens
from zion.logger import get_logger
from zion.utils.types import DictStrAny

logger = get_logger(__name__)

DbSessionDep = Annotated[AsyncSession, Depends()]
TokenDep = Annotated[str, Depends(settings.AUTH_OAUTH2_SCHEME)]


async def get_current_user(token: TokenDep, db: DbSessionDep) -> DictStrAny:
    token_data = tokens.verify(token, TokenType.ACCESS)
    if token_data is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    # TODO: fetch user with the given token data

    return {}


CurrentUserDep = Annotated[dict, Depends(get_current_user)]
