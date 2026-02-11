from abc import ABCMeta, abstractmethod


class PasswordServiceProtocol(metaclass=ABCMeta):
    @abstractmethod
    async def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def hash(self, password: str) -> str:
        raise NotImplementedError()
