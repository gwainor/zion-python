import abc
import datetime as dt

from zion.auth.enums import TokenType
from zion.auth.schemas import TokenData
from zion.utils.types import DictStrAny


class TokenServiceProtocol(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def create_access_token(
        self, data: DictStrAny, expires_delta: dt.timedelta | None = None
    ) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def create_refresh_token(
        self, data: DictStrAny, expires_delta: dt.timedelta | None = None
    ) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def verify(self, token: str, expected_token_type: TokenType) -> TokenData | None:
        raise NotImplementedError()
