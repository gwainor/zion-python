from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from zion_auth.deps import (
    DatabaseAdapterDep,
    PasswordServiceDep,
    TokenDep,
    TokenServiceDep,
    ValidationServiceDep,
)
from zion_auth.enums import CredentialType, TokenType
from zion_auth.exceptions import AuthenticationError, ValidationError
from zion_auth.models import User
from zion_auth.protocols import (
    ZionAuthServiceProtocol,
)
from zion_auth.settings import settings
from zion_logger import get_logger


logger = get_logger(__name__)


class ZionAuthService(ZionAuthServiceProtocol):
    def __init__(
        self,
        database: DatabaseAdapterDep,
        password_service: PasswordServiceDep,
        token_service: TokenServiceDep,
        validation_service: ValidationServiceDep,
    ):
        self.database = database
        self.password_service = password_service
        self.token_service = token_service
        self.validation_service = validation_service

    async def login(self, data: OAuth2PasswordRequestForm):
        credential = data.username
        credential_type = settings.credential_type

        try:
            # Get user based on credential type
            if credential_type == CredentialType.EMAIL:
                user = await self.database.get_by_email(credential)
            elif credential_type == CredentialType.USERNAME:
                user = await self.database.get_by_username(credential)
            elif credential_type == CredentialType.BOTH:
                user = await self.database.get_by_credential(credential)
            else:
                user = None

            if not user:
                return None

            # Verify password
            is_password_valid = await self.password_service.verify(
                data.password, user.hashed_password
            )
            if not is_password_valid:
                return None

            # Validate user
            is_user_valid = await self.validation_service.is_user_valid(user)
            if not is_user_valid:
                return None

            return user
        except ValidationError:
            return None
        except Exception as e:
            await logger.aerror("Login system error", error=str(e))
            raise AuthenticationError("Login system unavailable") from e

    async def get_current_user(self, token: TokenDep) -> User:
        token_data = await self.token_service.verify(token, TokenType.ACCESS)

        if not token_data:
            await logger.awarning("Could not verify access token", token=token)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        try:
            user = await self.database.get_by_public_id(token_data.public_id)
        except Exception as e:
            await logger.aerror("Login system error", error=str(e))
            raise AuthenticationError("Login system unavailable") from e

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        try:
            is_user_valid = await self.validation_service.is_user_valid(user)
        except ValidationError:
            is_user_valid = False
        except Exception as e:
            await logger.aerror("Login system error", error=str(e))
            raise AuthenticationError("Login system unavailable") from e

        if not is_user_valid:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return user

    async def get_optional_user(self, token: TokenDep) -> User | None:
        token_data = await self.token_service.verify(token, TokenType.ACCESS)

        if not token_data:
            return None

        try:
            user = await self.database.get_by_public_id(token_data.public_id)
        except Exception as e:
            await logger.aerror("Login system error", error=str(e))
            raise AuthenticationError("Login system unavailable") from e

        if not user:
            return None

        try:
            is_user_valid = await self.validation_service.is_user_valid(user)
        except ValidationError:
            is_user_valid = False
        except Exception as e:
            await logger.aerror("Login system error", error=str(e))
            raise AuthenticationError("Login system unavailable") from e

        if not is_user_valid:
            return None

        return user
