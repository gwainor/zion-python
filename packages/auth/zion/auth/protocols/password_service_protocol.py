import abc


class PasswordServiceProtocol(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    async def hash(self, password: str) -> str:
        raise NotImplementedError()
