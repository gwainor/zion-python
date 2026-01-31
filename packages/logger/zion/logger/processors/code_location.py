from collections.abc import Iterable

import structlog
from structlog.typing import Processor


class CodeLocation:
    """Inject the location of the logging message into the logs"""

    def setup(self) -> Iterable[Processor]:
        # Add callsite parameters
        call_site_proc = structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        )

        return [call_site_proc]


__all__ = ["CodeLocation"]
