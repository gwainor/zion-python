import os
from typing import Any

from zion.config.constants import ENVIRONMENT_VARIABLE
from zion.config.utils import import_attribute


class AppConfOptions:
    names: dict[str, str]

    def __init__(self, meta, prefix: str):
        self.prefix = prefix
        env_settings = os.environ.get(ENVIRONMENT_VARIABLE, None)
        self.holder_path = getattr(meta, "holder", env_settings)
        self.holder = import_attribute(self.holder_path)
        self.required = getattr(meta, 'required', [])
        self.names = {}
        self.defaults = {}
        self.configured_data = {}

    def prefixed_name(self, name: str):
        if name.startswith(self.prefix.upper()):
            return name
        return f"{self.prefix.upper()}_{name.upper()}"


class AppConfMetaClass(type):
    _meta: AppConfOptions

    def __new__(cls, config_name, bases, attrs):
        super_new = super().__new__
        parents = [base for base in bases if isinstance(base, AppConfMetaClass)]
        if not parents:
            return super_new(cls, config_name, bases, attrs)

        module = attrs.pop("__module__")
        new_class = super_new(cls, config_name, bases, {"__module__": module})
        attr_meta = attrs.pop("Meta", None)
        if attr_meta:
            meta = attr_meta
        else:
            attr_meta = type("Meta", (object,), {})
            meta = getattr(new_class, "Meta", None)

        prefix = getattr(meta, "prefix", None)

        if prefix is None:
            raise ValueError("`app_label` or `prefix` must be defined in the AppConf Meta!")

        new_class._meta = AppConfOptions(meta, prefix)

        for parent in parents[::-1]:
            if not hasattr(parent, "_meta"):
                continue

            new_class._meta.names.update(parent._meta.names)
            new_class._meta.defaults.update(parent._meta.defaults)
            new_class._meta.configured_data.update(parent._meta.configured_data)

        attr_names = list(attrs.keys())
        config_names = filter(str.isupper, attr_names)
        for config_name in config_names:
            prefixed_config_name = new_class._meta.prefixed_name(config_name)
            new_class._meta.names[config_name] = prefixed_config_name
            new_class._meta.defaults[prefixed_config_name] = attrs.pop(config_name)

        for name, value in attrs.items():
            setattr(new_class, name, value)

        from zion.config import settings
        new_class._configure()
        for name, value in new_class._meta.configured_data.items():
            prefixed_config_name = new_class._meta.prefixed_name(name)
            setattr(settings, prefixed_config_name, value)
            setattr(new_class, name, value)

        for name in new_class._meta.required:
            prefixed_config_name = new_class._meta.prefixed_name(name)
            if not hasattr(new_class._meta.holder, prefixed_config_name):
                raise ValueError(f"The required setting {prefixed_config_name} is missing.")

        return new_class

    def _configure(cls):
        conf = cls()
        for name, prefixed_name in conf._meta.names.items():
            default_value = conf._meta.defaults.get(prefixed_name)
            value = getattr(conf._meta.holder, prefixed_name, default_value)

            callback = getattr(conf, f"configure_{name.lower()}", None)
            if callable(callback):
                value = callback(value)

            cls._meta.configured_data[name] = value
        cls._meta.configured_data = conf.configure()


class AppConf(metaclass=AppConfMetaClass):
    _meta: AppConfOptions

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __dir__(self):
        return sorted(set(self._meta.names.keys()))

    @property
    def configured_data(self):
        return self._meta.configured_data

    def __setattr__(self, name: str, value: Any) -> None:
        if name.isupper():
            setattr(self._meta.holder, self._meta.prefixed_name(name), value)
        object.__setattr__(self, name, value)

    def configure(self):
        return self.configured_data

