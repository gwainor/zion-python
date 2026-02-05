from zion.auth.models import User


def is_deleted(user: User) -> bool:
    """Validates user if soft deleted or not."""
    return not user.is_deleted
