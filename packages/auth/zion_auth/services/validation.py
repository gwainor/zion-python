import inspect
from collections.abc import Awaitable, Callable
from functools import cached_property

from zion_auth.exceptions import ValidationError
from zion_auth.models import User
from zion_auth.protocols import ValidationServiceProtocol
from zion_auth.settings import settings
from zion_utils.module_loading import import_string


class ValidationService(ValidationServiceProtocol):
    _user_validators: list[Callable[[User], Awaitable[bool] | bool]] = []

    async def is_user_valid(self, user: User) -> bool:
        self._load_user_validators()

        try:
            for validator in self._user_validators:
                if inspect.iscoroutinefunction(validator):
                    is_valid = await validator(user)
                else:
                    is_valid = validator(user)

                if is_valid is False:
                    return is_valid
        except (ValueError, AttributeError, ValidationError) as e:
            raise ValidationError(str(e)) from e

        return True

    @cached_property
    def _load_user_validators(self):
        if not self._user_validators:
            return

        for validator in settings.user_validators:
            self._user_validators.append(import_string(validator))
