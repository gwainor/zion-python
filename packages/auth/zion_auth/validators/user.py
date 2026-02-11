from zion_auth.models import User


def is_active(user: User) -> bool:
    return user.is_active and not user.is_deleted
