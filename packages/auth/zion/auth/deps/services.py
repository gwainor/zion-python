from typing import Annotated

from fastapi import Depends
from zion.auth.conf import settings
from zion.auth.protocols import (
    AuthValidationServiceProtocol,
    TokenServiceProtocol,
    UserServiceProtocol,
)
from zion.db import DbSessionDep
from zion.utils.module_loading import import_string

from .helpers import UserValidatorsDep


def get_user_service(session: DbSessionDep) -> UserServiceProtocol:
    UserServiceCls: type[UserServiceProtocol] = import_string(
        settings.AUTH_SERVICES.USER
    )
    return UserServiceCls(session)


UserServiceDep = Annotated[UserServiceProtocol, Depends(get_user_service)]


def get_auth_token_service() -> TokenServiceProtocol:
    TokenServiceCls: type[TokenServiceProtocol] = import_string(
        settings.AUTH_SERVICES.TOKEN
    )
    return TokenServiceCls()


AuthTokenServiceDep = Annotated[TokenServiceProtocol, Depends(get_auth_token_service)]


def get_auth_validation_service(
    user_validators: UserValidatorsDep,
) -> AuthValidationServiceProtocol:
    AuthValidationServiceCls: type[AuthValidationServiceProtocol] = import_string(
        settings.AUTH_SERVICES.AUTH_VALIDATION
    )
    return AuthValidationServiceCls(user_validators=user_validators)


AuthValidationServiceDep = Annotated[
    AuthValidationServiceProtocol, Depends(get_auth_validation_service)
]
