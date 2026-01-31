from structlog.typing import EventDict, Processor, WrappedLogger


class LoggerName:
    """Sets the logger name in the logs"""

    def setup(self) -> list[Processor]:
        return [self]

    def __call__(
        self, logger: WrappedLogger, method_name: str, event_dict: EventDict
    ) -> EventDict:
        if event_dict.get("logger_name") is not None:
            event_dict["logger"] = event_dict.pop("logger_name")
        return event_dict


__all__ = ["LoggerName"]
