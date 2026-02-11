import datetime as dt
from abc import ABCMeta, abstractmethod

from zion_auth.enums import TokenType
from zion_auth.models import TokenData
from zion_utils.types import DictStrAny


class TokenServiceProtocol(metaclass=ABCMeta):
    @abstractmethod
    async def create_access_token(
        self, data: DictStrAny, expires_delta: dt.timedelta | None = None
    ) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def create_refresh_token(
        self, data: DictStrAny, expires_delta: dt.timedelta | None = None
    ) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def verify(
        self, token: str, expected_token_type: TokenType
    ) -> TokenData | None:
        raise NotImplementedError()
