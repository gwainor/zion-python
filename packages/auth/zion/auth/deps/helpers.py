import functools
from typing import Annotated

from fastapi import Depends
from zion.auth.conf import settings
from zion.auth.protocols.auth_validation_service_protocol import UserValidatorFunc
from zion.utils.exceptions import ImproperlyConfiguredError
from zion.utils.module_loading import import_string


@functools.cache
def get_default_user_validators() -> list[UserValidatorFunc]:
    return get_user_validators(settings.AUTH_USER_VALIDATORS)


def get_user_validators(validator_config: list[str]) -> list[UserValidatorFunc]:
    validators = []
    for validator in validator_config:
        try:
            func = import_string(validator)
        except ImportError:
            msg = (
                f"The module {validator} could not be imported. Check your "
                "AUTH_USER_VALIDATORS setting."
            )
            raise ImproperlyConfiguredError(msg)
        validators.append(func)

    return validators


UserValidatorsDep = Annotated[list[UserValidatorFunc], Depends(get_user_validators)]
