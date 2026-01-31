import functools
import inspect
from collections.abc import Callable
from dataclasses import is_dataclass
from typing import Any, Literal, cast

from .logger import get_logger

local_logger = get_logger(__name__)


class log[T: Callable[..., Any]]:
    logger: Any
    sanitize_params: list[str]
    expected_errors: list[type[Exception]]
    log_level: Literal["debug", "info"]

    def __init__(
        self,
        sanitize_params: list[str] | None = None,
        expected_errors: list[type[Exception]] | None = None,
        logger: Any | None = None,
        level: Literal["debug", "info"] = "debug",
    ) -> None:
        self.logger = logger or local_logger
        self.sanitize_params = sanitize_params or []
        self.expected_errors = expected_errors or []
        self.log_level = level

    def __call__(self, func: T) -> T:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                target_name, sanitized = self._build_log_vars(func, args, kwargs)
                log_func = self.get_log_func(True)

                try:
                    result = await func(*args, **kwargs)
                    await log_func(
                        f"Called: {target_name}", input=sanitized, return_value=result
                    )
                    return result
                except Exception as e:
                    if isinstance(e, tuple(self.expected_errors)):
                        await log_func(
                            f"Called: {target_name}, raised expected error",
                            input=sanitized,
                            error=str(e),
                        )
                    else:
                        await self.logger.aerror(
                            f"Called {target_name}, raised unexpected error",
                            input=sanitized,
                            error=str(e),
                        )
                    raise
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                target_name, sanitized = self._build_log_vars(func, args, kwargs)
                log_func = self.get_log_func(False)

                try:
                    result = func(*args, **kwargs)
                    log_func(
                        f"Called: {target_name}", input=sanitized, return_value=result
                    )
                    return result
                except Exception as e:
                    if isinstance(e, tuple(self.expected_errors)):
                        log_func(
                            f"Called: {target_name}, raised expected error",
                            input=sanitized,
                            error=str(e),
                        )
                    else:
                        self.logger.error(
                            f"Called {target_name}, raised unexpected error",
                            input=sanitized,
                            error=str(e),
                        )
                    raise

        return cast(T, wrapper)

    def get_log_func(self, is_async: bool) -> Callable[..., Any]:
        match self.log_level:
            case "debug":
                return self.logger.adebug if is_async else self.logger.debug
            case "info":
                return self.logger.ainfo if is_async else self.logger.info
            case _:
                raise ValueError(f"Unknown log level {self.log_level}")

    def _build_log_vars(
        self, func: T, args: tuple, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Hide values of the given keys in the log data"""
        target_name = func.__name__
        if self._is_class_method(args):
            class_name = args[0].__class__.__name__
            target_name = f"{class_name}::{target_name}"

        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()

        sanitized_params = {}
        for key, value in bound.arguments.items():
            if key in self.sanitize_params:
                sanitized_params[key] = "*" * 10
            elif is_dataclass(value):
                sanitized_params[key] = repr(value)
            else:
                sanitized_params[key] = value

        return target_name, sanitized_params

    @staticmethod
    def _is_class_method(args: tuple) -> bool:
        """Check if the function is a class method by examining the first argument."""
        return (
            bool(args)
            and hasattr(args[0], "__class__")
            and not isinstance(args[0], (int, float, str, list, dict, tuple))
        )
