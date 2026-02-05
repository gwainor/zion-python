import inspect

from zion.auth.models import User
from zion.auth.protocols import AuthValidationServiceProtocol
from zion.logger import get_logger

logger = get_logger(__name__)


class AuthValidationService(AuthValidationServiceProtocol):
    async def is_user_valid(self, user: User) -> bool:
        for user_validator in self.user_validators:
            if inspect.iscoroutinefunction(user_validator):
                is_valid = await user_validator(user)
            else:
                is_valid = user_validator(user)

            if not is_valid:
                await logger.awarning(
                    f"User validation failed by {getattr(user_validator, '__name__', repr(user_validator))}"
                )
                return False

        return True


__all__ = ["AuthValidationService"]
