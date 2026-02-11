__all__ = ["ZionAuth"]


def __getattr__(name):
    if name == "ZionAuth":
        from .deps.main import ZionAuth

        return ZionAuth
    raise AttributeError(name)
