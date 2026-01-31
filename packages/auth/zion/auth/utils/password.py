import bcrypt


async def verify(plain_password: str, hashed_password: str) -> bool:
    is_password_correct: bool = bcrypt.checkpw(
        plain_password.encode(), hashed_password.encode()
    )
    return is_password_correct


def generate_hash(password: str) -> str:
    hashed_password: str = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashed_password
