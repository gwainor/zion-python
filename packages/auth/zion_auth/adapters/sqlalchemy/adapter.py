from typing import Annotated

from fastapi import Depends

from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from zion_auth.models import User
from zion_auth.protocols.database_adapter import DatabaseAdapterProtocol
from zion_auth.utils import import_dependency
from zion_logger import get_logger

from .models import UserSqlModel


logger = get_logger(__name__)


SessionDep = Annotated[
    AsyncSession,
    Depends(
        import_dependency(
            "database_session_dep",
            no_setting_error="`database_session_dep` value must be provided when using with sqlalchemy adapter.",
        )
    ),
]


class SqlAlchemyAdapter(DatabaseAdapterProtocol):
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        try:
            user = await self.session.get_one(
                UserSqlModel, UserSqlModel.username == username
            )
            return self._convert_user_model(user)
        except NoResultFound:
            return None
        except SQLAlchemyError as error:
            await logger.aerror(
                "Database error on SqlAlchemyAdapter::get_by_username()",
                username=username,
                error=str(error),
            )
            raise

    async def get_by_email(self, email: str) -> User | None:
        try:
            user = await self.session.get_one(UserSqlModel, UserSqlModel.email == email)
            return self._convert_user_model(user)
        except NoResultFound:
            return None
        except SQLAlchemyError as error:
            await logger.aerror(
                "Database error on SqlAlchemyAdapter::get_by_email()",
                email=email,
                error=str(error),
            )
            raise

    async def get_by_id(self, id: int) -> User | None:
        try:
            user = await self.session.get(UserSqlModel, id)
            if user:
                return self._convert_user_model(user)
            else:
                return None
        except SQLAlchemyError as error:
            await logger.aerror(
                "Database error on SqlAlchemyAdapter::get_by_id()",
                id=id,
                error=str(error),
            )
            raise

    async def get_by_public_id(self, id: str) -> User | None:
        try:
            user = await self.session.get_one(UserSqlModel, UserSqlModel.pid == id)
            return self._convert_user_model(user)
        except SQLAlchemyError as error:
            await logger.aerror(
                "Database error on SqlAlchemyAdapter::get_by_public_id()",
                id=id,
                error=str(error),
            )
            raise

    async def get_by_credential(self, credential: str) -> User | None:
        try:
            user = await self.session.get_one(
                UserSqlModel,
                or_(
                    UserSqlModel.email == credential,
                    UserSqlModel.username == credential,
                ),
            )
            return self._convert_user_model(user)
        except NoResultFound:
            return None
        except SQLAlchemyError as error:
            await logger.aerror(
                "Database error on SqlAlchemyAdapter::get_by_credential()",
                credential=credential,
                error=str(error),
            )
            raise

    def _convert_user_model(self, sql_model: UserSqlModel) -> User:
        return User.model_validate(UserSqlModel)
