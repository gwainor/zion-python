import abc

from sqlalchemy.ext.asyncio import AsyncSession
from zion.auth.models import User


class UserServiceProtocol(metaclass=abc.ABCMeta):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @abc.abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_credential(self, credential: str) -> User | None:
        raise NotImplementedError


__all__ = ["UserServiceProtocol"]
