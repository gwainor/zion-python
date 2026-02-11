from abc import ABCMeta, abstractmethod

from zion_auth.models import User


class ValidationServiceProtocol(metaclass=ABCMeta):
    @abstractmethod
    async def is_user_valid(self, user: User) -> bool:
        raise NotImplementedError()
