import datetime as dt

from jose import JWTError, jwt

from zion_auth.enums import TokenType
from zion_auth.models import TokenData
from zion_auth.protocols import TokenServiceProtocol
from zion_auth.settings import settings
from zion_utils.types import DictStrAny


class TokenService(TokenServiceProtocol):
    async def _create(
        self,
        token_type_str: TokenType,
        data: DictStrAny,
        expires_delta: dt.timedelta | None = None,
    ) -> str:
        token_type = TokenType(token_type_str)

        if not expires_delta:
            match token_type:
                case TokenType.ACCESS:
                    delta = dt.timedelta(minutes=settings.access_token_expire_minutes)
                case TokenType.REFRESH:
                    delta = dt.timedelta(days=settings.refresh_token_expire_days)
                case _:
                    raise ValueError(f"Unknown token type provided: {token_type}")
        else:
            delta: dt.timedelta = expires_delta

        expire = dt.datetime.now(dt.UTC) + delta

        to_encode = data.copy()
        to_encode.update({"exp": expire, "token_type": token_type})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key.get_secret_value(),
            algorithm=settings.token_algorithm,
        )

        return encoded_jwt

    async def create_access_token(
        self, data: DictStrAny, expires_delta: dt.timedelta | None = None
    ) -> str:
        return await self._create(TokenType.ACCESS, data, expires_delta)

    async def create_refresh_token(
        self, data: DictStrAny, expires_delta: dt.timedelta | None = None
    ) -> str:
        return await self._create(TokenType.REFRESH, data, expires_delta)

    async def verify(
        self, token: str, expected_token_type: TokenType
    ) -> TokenData | None:
        try:
            payload = jwt.decode(
                token,
                settings.secret_key.get_secret_value(),
                algorithms=[settings.token_algorithm],
            )
            public_id: str | None = payload.get("sub")
            token_type: TokenType = TokenType(payload.get("token_type"))

            if not public_id or token_type != expected_token_type:
                return None

            return TokenData(public_id=public_id)
        except (JWTError, ValueError):
            return None


__all__ = ["TokenService"]
