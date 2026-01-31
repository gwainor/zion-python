import functools
import hashlib
import inspect
from collections.abc import Callable
from dataclasses import is_dataclass
from typing import Any, TypeVar, cast

from structlog import BoundLogger

T = TypeVar("T", bound=Callable[..., Any])


def is_class_method(args: tuple) -> bool:
    """
    Check if the function is a class method by examining the first argument.
    """
    return (
        bool(args)
        and hasattr(args[0], "__class__")
        and not isinstance(args[0], (int, float, str, list, dict, tuple))
    )


def convert_args_to_kwargs(func: Callable, args: tuple, kwargs: dict) -> dict:
    """
    Convert all arguments to keyword arguments for better logging.
    """
    param_names = list(inspect.signature(func).parameters.keys())
    if is_class_method(args):
        param_names = param_names[1:]
        args = args[1:]
    all_kwargs = dict(zip(param_names, args))
    all_kwargs.update(kwargs)
    return all_kwargs


def sanitize_kwargs(kwargs: dict, keys: list[str]) -> dict:
    """Hide values of the given keys in the log data"""
    result = {}
    for key, value in kwargs.items():
        if key in keys:
            result[key] = hashlib.md5(str(value).encode()).hexdigest()
        else:
            if is_dataclass(value):
                result[key] = value.__repr__()
            else:
                result[key] = value
    return result


def build_log_vars(
    func: Callable[..., Any], args, kwargs, sanitize_params: list[str]
) -> tuple[dict[str, Any], str]:
    all_kwargs = convert_args_to_kwargs(func, args, kwargs)
    sanitized_kwargs = sanitize_kwargs(all_kwargs, sanitize_params)

    target_name = func.__name__
    if is_class_method(args):
        class_name = args[0].__class__.__name__
        target_name = f"{class_name}::{target_name}"

    return sanitized_kwargs, target_name


def log(
    logger: BoundLogger,
    sanitize_params: list[str] | None = None,
    expected_exceptions: list[type[Exception]] | None = None,
) -> Callable[[T], T]:
    sanitize_params = sanitize_params or []
    expected_exceptions = expected_exceptions or []

    def decorator(func: T) -> T:
        if inspect.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs) -> T:
                sanitized_kwargs, target_name = build_log_vars(
                    func, args, kwargs, sanitize_params
                )

                try:
                    result = await func(*args, **kwargs)
                    message = f"Called: {target_name}"
                    await logger.adebug(
                        message, input=sanitized_kwargs, return_value=result
                    )
                    return result
                except Exception as e:
                    if not isinstance(e, tuple(expected_exceptions)):
                        await logger.aexception(
                            f"{target_name} has raised an unexpected error",
                            input=sanitized_kwargs,
                            error=str(e),
                        )
                    else:
                        await logger.adebug(
                            f"{target_name} raised an expected error",
                            input=sanitized_kwargs,
                            error=str(e),
                        )
                    raise e

            return cast(T, wrapper)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            sanitized_kwargs, target_name = build_log_vars(
                func, args, kwargs, sanitize_params
            )

            try:
                result = func(*args, **kwargs)
                message = f"Called: {target_name}"
                logger.debug(message, input=sanitized_kwargs, return_value=result)
                return result
            except Exception as e:
                if not isinstance(e, tuple(expected_exceptions)):
                    logger.exception(
                        f"{target_name} has raised an unexpected error",
                        input=sanitized_kwargs,
                        error=str(e),
                    )
                else:
                    logger.debug(
                        f"{target_name} raised an expected error",
                        input=sanitized_kwargs,
                        error=str(e),
                    )
                raise e

        return cast(T, wrapper)

    return decorator
