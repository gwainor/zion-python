from abc import ABCMeta, abstractmethod

from fastapi.security import OAuth2PasswordRequestForm

from zion_auth.deps import TokenDep
from zion_auth.models import User


class ZionAuthServiceProtocol(metaclass=ABCMeta):
    @abstractmethod
    async def login(self, data: OAuth2PasswordRequestForm):
        raise NotImplementedError()

    @abstractmethod
    async def get_current_user(self, token: TokenDep) -> User:
        raise NotImplementedError()
