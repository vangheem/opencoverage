import time
import traceback
from functools import wraps
from typing import Dict, Optional, Type

from prometheus_client import Counter, Histogram

ERROR_NONE = "none"
ERROR_GENERAL_EXCEPTION = "exception"

OPS = Counter(
    "opencoverage_ops_total",
    "Total count of ops by type of operation and the error if there was.",
    labelnames=["type", "error"],
)
OPS_PROCESSING_TIME = Histogram(
    "opencoverage_ops_processing_time_seconds",
    "Histogram of operations processing time by type (in seconds)",
    labelnames=["type"],
)


class _watch:
    start: float

    def __init__(
        self,
        *,
        counter: Optional[Counter] = None,
        histogram: Optional[Histogram] = None,
        error_mappings: Dict[str, Type[Exception]] = None,
        labels: Optional[Dict[str, str]] = None,
    ):
        self.counter = counter
        self.histogram = histogram
        self.labels = labels or {}
        self.error_mappings = error_mappings or {}

    def __call__(self, func):
        """
        decorator version
        """

        @wraps(func)
        async def inner(*args, **kwargs):
            with self:
                return await func(*args, **kwargs)

        return inner

    def __enter__(self):
        self.start = time.time()

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        exc_traceback: Optional[traceback.StackSummary],
    ):
        error = ERROR_NONE
        if self.histogram is not None:
            finished = time.time()
            if len(self.labels) > 0:
                self.histogram.labels(**self.labels).observe(finished - self.start)
            else:
                self.histogram.observe(finished - self.start)

        if self.counter is not None:
            if exc_value is None:
                error = ERROR_NONE
            else:
                for error_type, mapped_exc_type in self.error_mappings.items():
                    if isinstance(exc_value, mapped_exc_type):
                        error = error_type
                        break
                else:
                    error = ERROR_GENERAL_EXCEPTION
            self.counter.labels(error=error, **self.labels).inc()


class watch(_watch):
    def __init__(self, operation: str):
        super().__init__(
            counter=OPS,
            histogram=OPS_PROCESSING_TIME,
            labels={"type": operation},
        )
