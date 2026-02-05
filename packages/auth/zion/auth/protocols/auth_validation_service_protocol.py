import abc
from collections.abc import Callable

from zion.auth.models import User

UserValidatorFunc = Callable[[User], bool]


class AuthValidationServiceProtocol(metaclass=abc.ABCMeta):
    def __init__(self, user_validators: list[UserValidatorFunc]):
        self.user_validators = user_validators

    @abc.abstractmethod
    async def is_user_valid(self, user: User) -> bool:
        """Validates user with the given validators.
        Accepts a list of validator function which must return a boolean value.
        The execution will stop as soon as a validator returns `False`.

        Args:
            user (REQUIRED): The user to run validations against
            validators (OPTIONAL): A list of validator callables.
              If none given, it will use the validators in `AUTH_USER_VALIDATORS`
        """
        raise NotImplementedError()
