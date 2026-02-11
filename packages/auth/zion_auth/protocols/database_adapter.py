from abc import ABCMeta, abstractmethod

from zion_auth.models import User


class DatabaseAdapterProtocol(metaclass=ABCMeta):
    @abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_public_id(self, id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_credential(self, credential: str) -> User | None:
        raise NotImplementedError


__all__ = ["DatabaseAdapterProtocol"]
