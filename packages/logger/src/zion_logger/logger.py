import logging

import orjson
import structlog
from structlog.typing import Processor

from . import processors


def initialize_logger(
    custom_processors: list[Processor] | None = None,
    cache_logger_on_first_use: bool = True,
):
    if custom_processors is None:
        custom_processors = []

    structlog.configure(
        cache_logger_on_first_use=cache_logger_on_first_use,
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        processors=[
            *processors.LoggerName().setup(),
            *processors.CodeLocation().setup(),
            *custom_processors,
            # Need to add JSONRenderer as the last processor since orjson serializes
            # to bytes for performance reasons.
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        logger_factory=structlog.BytesLoggerFactory(),
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    if name is not None:
        logger = structlog.get_logger(logger_name=name)
    else:
        logger = structlog.get_logger()

    return logger


__all__ = ["get_logger", "initialize_logger"]
