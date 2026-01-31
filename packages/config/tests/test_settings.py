import os

import pytest


def test_settings_is_loading_from_environment_variable():
    os.environ["ZION_SETTINGS_MODULE"] = "tests.settings"
    from zion.config import settings

    assert settings.SIMPLE_VALUE is True


def test_settings_throwing_error_if_module_not_found():
    os.environ["ZION_SETTINGS_MODULE"] = "non_existent.module.settings"
    from zion.config import _Settings

    with pytest.raises(ImportError):
        _Settings()
