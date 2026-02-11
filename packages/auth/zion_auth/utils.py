from zion_auth.exceptions import ImproperlyConfiguredError
from zion_auth.settings import settings
from zion_utils.module_loading import import_string


def import_dependency(
    setting_name: str,
    no_setting_error: str | None = None,
    import_error: str | None = None,
):
    module_str = getattr(settings, setting_name, None)
    if not module_str:
        raise ImproperlyConfiguredError(
            no_setting_error or f"settings::{setting_name} must be provided."
        )

    try:
        return import_string(module_str)
    except ImportError as e:
        raise ImproperlyConfiguredError(
            import_error
            or f"settings::{setting_name} module cannot be imported. The value is: {module_str}"
        ) from e
