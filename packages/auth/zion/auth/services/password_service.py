import bcrypt
from zion.auth.protocols import PasswordServiceProtocol


class PasswordService(PasswordServiceProtocol):
    async def verify(self, plain_password: str, hashed_password: str) -> bool:
        is_password_correct: bool = bcrypt.checkpw(
            plain_password.encode(), hashed_password.encode()
        )
        return is_password_correct

    async def hash(self, password: str) -> str:
        hashed_password: str = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()
        return hashed_password
