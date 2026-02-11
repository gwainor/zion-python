from zion_auth.exceptions import ImproperlyConfiguredError


try:
    import sqlalchemy  # noqa
except ImportError as e:
    raise ImproperlyConfiguredError(
        "No SqlAlchemy installation found while the db_adapter is set to sqlalchemy"
    ) from e

from .adapter import SqlAlchemyAdapter


__all__ = ["SqlAlchemyAdapter"]
