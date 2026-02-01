from zion.config import AppConf, settings


class Conf(AppConf):
    DATABASE_URI = ""
    MODEL_MODULES: list[str] = []

    class Meta:
        prefix = "db"


__all__ = ["settings"]
