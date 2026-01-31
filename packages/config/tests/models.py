from zion.config import AppConf


class TestConf(AppConf):
    SIMPLE_VALUE = True
    CONFIGURED_VALUE = "wrong"

    class Meta:
        app_label = "test"

    def configure_configured_value(self, value):
        return "correct"

    def configure(self):
        self.configured_data["CONFIGURE_METHOD_VALUE"] = True
        return self.configured_data
