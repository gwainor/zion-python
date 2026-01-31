import importlib
import os
from typing import TYPE_CHECKING, Any

from .app_conf import AppConf
from .constants import ENVIRONMENT_VARIABLE


class _Settings:
    CONFIG_MODULE_NAME: str

    def __init__(self):
        config_module_name = os.environ.get(ENVIRONMENT_VARIABLE)
        if not config_module_name:
            raise ImportError(
                "Cannot find config module! "
                "Please make sure that you have defined the environment variable "
                f"{ENVIRONMENT_VARIABLE}."
            )

        self.configure(config_module_name)

    def configure(self, config_module_name: str):
        self.CONFIG_MODULE_NAME = config_module_name

        mod = importlib.import_module(self.CONFIG_MODULE_NAME)

        for config_name in dir(mod):
            if not config_name.isupper():
                continue

            config_value = getattr(mod, config_name)
            setattr(self, config_name, config_value)

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.CONFIG_MODULE_NAME}">'


if TYPE_CHECKING:
    class _SettingsObject:
        def __getattr__(self, item: Any) -> Any: ...


    class _Settings(_SettingsObject): ...


settings = _Settings()


__all__ = [
    "settings",
    "AppConf",
]


