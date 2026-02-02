from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from zion.auth.models import User
from zion.auth.protocols import UserServiceProtocol


class UserService(UserServiceProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        try:
            user = await self.session.get_one(User, User.username == username)
            return user
        except NoResultFound:
            return None

    async def get_by_email(self, email: str) -> User | None:
        try:
            user = await self.session.get_one(User, User.email == email)
            return user
        except NoResultFound:
            return None

    async def get_by_id(self, id: int) -> User | None:
        user = await self.session.get(User, id)
        return user

    async def get_by_credential(self, credential: str) -> User | None:
        try:
            user = await self.session.get_one(
                User, or_(User.email == credential, User.username == credential)
            )
            return user
        except NoResultFound:
            return None


__all__ = ["UserService"]
