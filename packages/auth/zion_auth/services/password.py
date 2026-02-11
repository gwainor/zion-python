import asyncio

import bcrypt

from zion_auth.protocols import PasswordServiceProtocol


class PasswordService(PasswordServiceProtocol):
    async def verify(self, plain_password: str, hashed_password: str) -> bool:
        is_password_correct: bool = await asyncio.to_thread(
            bcrypt.checkpw,
            plain_password.encode(),
            hashed_password.encode(),
        )
        return is_password_correct

    async def hash(self, password: str) -> str:
        hashed_password_bytes: bytes = await asyncio.to_thread(
            bcrypt.hashpw,
            password.encode(),
            bcrypt.gensalt(),
        )
        return hashed_password_bytes.decode()


__all__ = ["PasswordService"]
