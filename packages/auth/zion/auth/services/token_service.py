import datetime as dt

from jose import JWTError, jwt
from zion.auth.conf import settings
from zion.auth.enums import TokenType
from zion.auth.protocols import TokenServiceProtocol
from zion.auth.schemas import TokenData
from zion.utils.types import DictStrAny


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
                    delta = dt.timedelta(
                        minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                case TokenType.REFRESH:
                    delta = dt.timedelta(days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS)
                case _:
                    raise ValueError(f"Unknwon token type provided: {token_type}")
        else:
            delta: dt.timedelta = expires_delta

        expire = dt.datetime.now(dt.UTC).replace(tzinfo=None) + delta

        to_encode = data.copy()
        to_encode.update({"exp": expire, "token_type": token_type})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.AUTH_SECRET_KEY.get_secret_value(),
            algorithm=settings.AUTH_ALGORITHM,
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

    def verify(self, token: str, expected_token_type: TokenType) -> TokenData | None:
        try:
            payload = jwt.decode(
                token,
                settings.AUTH_SECRET_KEY.get_secret_value(),
                algorithms=[settings.AUTH_ALGORITHM],
            )
            credential: str | None = payload.get("sub")
            token_type: TokenType = TokenType(payload.get("token_type"))

            if not credential or token_type != expected_token_type:
                return None

            return TokenData(credential=credential)
        except (JWTError, ValueError):
            return None
