import pytest


def test_basic_functionality():
    from zion.config import AppConf, settings

    class Conf(AppConf):
        SOME_CONFIG = "some value"

        class Meta:
            prefix = "auth"

    assert settings.AUTH_SOME_CONFIG == "some value"


def test_appconf_uses_value_from_setting_file():
    from zion.config import AppConf, settings

    class Conf(AppConf):
        SOME_CONFIG = True
        SOME_SETTING = "some value"

        class Meta:
            prefix = "test"

    assert settings.TEST_SOME_CONFIG is True
    assert Conf.SOME_CONFIG is True

    assert settings.TEST_SOME_SETTING == "overriden value"
    assert Conf.SOME_SETTING == "overriden value"


def test_appconf_meta_required_passes():
    from zion.config import AppConf, settings

    # User must define `TEST_SOME_SETTING` in the settings
    class Conf(AppConf):
        SOME_OTHER_SETTING = "some value"

        class Meta:
            prefix = "test"
            required = ["SOME_SETTING"]

    assert settings.TEST_SOME_SETTING == "overriden value"


def test_appconf_meta_required_throws_error():
    from zion.config import AppConf

    # User must define `TEST_REQUIRED_FIELD` in the settings
    with pytest.raises(ValueError):

        class Conf(AppConf):
            SOME_SETTING = "some value"

            class Meta:
                prefix = "test"
                required = ["REQUIRED_FIELD"]


def test_configure_method_overrides_setting_module_value():
    from zion.config import AppConf, settings

    class Conf(AppConf):
        SOME_SETTING = "some value"
        CONFIGURED_SETTING = "correct"

        class Meta:
            prefix = "test"

        def configure_configured_setting(self, value):
            # The value coming from settings module
            assert value == "wrong"

            # Overriding the value
            return "something"

    assert settings.TEST_CONFIGURED_SETTING == "something"
    assert Conf.CONFIGURED_SETTING == "something"


def test_configure_method_overrides():
    from zion.config import AppConf, settings

    class Conf(AppConf):
        NEW_SETTING = "some value"

        class Meta:
            prefix = "test"

        def configure_new_setting(self, value):
            # The value should come from this `NEW_SETTING` because
            # it is not defined in the settings module
            assert value == "some value"

            # Overriding the value
            return "something"

    assert settings.TEST_NEW_SETTING == "something"
    assert Conf.NEW_SETTING == "something"
