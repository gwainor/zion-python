from types import SimpleNamespace

import pytest

from zion_auth.exceptions import ImproperlyConfiguredError
from zion_auth.utils import import_dependency

from .mock import MockClass


@pytest.fixture
def override_settings(monkeypatch: pytest.MonkeyPatch):
    def wrapper(**kwargs):
        kwargs["db_adapter_dep"] = "test.utils.mock.MockClass"
        fake_settings = SimpleNamespace(**kwargs)
        monkeypatch.setattr("zion_auth.utils.settings", fake_settings)
        return fake_settings

    return wrapper


def test_success(override_settings):
    # Given
    override_settings(foo_module="tests.utils.mock.MockClass")

    # When
    dependency = import_dependency("foo_module")

    # Then
    assert dependency is not None
    instance = dependency()
    assert instance is not None
    assert isinstance(instance, MockClass)


def test_raises_error_if_setting_not_found(override_settings):
    # Given
    override_settings(foo="bar")

    # When / Then
    with pytest.raises(ImproperlyConfiguredError):
        import_dependency("unknown_setting")


def test_raises_error_with_given_str_if_setting_not_found(override_settings):
    # Given
    override_settings(foo="bar")

    # When / Then
    with pytest.raises(ImproperlyConfiguredError) as e:
        err_message = "test message"
        import_dependency("unknown_setting", no_setting_error=err_message)
        assert err_message in str(e)


def test_raises_error_if_module_not_found(override_settings):
    # Given
    override_settings(foo_module="tests.utils.mock.unknown")

    # When / Then
    with pytest.raises(ImproperlyConfiguredError):
        import_dependency("foo_module")


def test_raises_error_with_given_str_if_module_not_found(override_settings):
    # Given
    override_settings(foo_module="tests.utils.mock.unknown")

    # When / Then
    with pytest.raises(ImproperlyConfiguredError) as e:
        err_message = "test message"
        import_dependency("foo_module", import_error=err_message)
        assert err_message in str(e)
