import time
from contextlib import contextmanager

from benchmark.src.datatypes.utils_dt import TimeStats


def now() -> float:
    return time.perf_counter()


@contextmanager
def timed():
    start = time.perf_counter()
    result = {}
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start



def summarize_time_measure(values: list[float]) -> TimeStats:
    """
    calculate mean, stdev, min, max for time measurement in benchmarks
    """
    if len(values) == 1:
        single_value = values[0]
        return TimeStats(
            mean=single_value,
            stdev=0.0,
            min_value=single_value,
            max_value=single_value,
        )

    average_value = sum(values) / len(values)
    variance = sum((value - average_value) ** 2 for value in values) / (len(values) - 1)

    return TimeStats(
        mean=average_value,
        stdev=variance ** 0.5,
        min_value=min(values),
        max_value=max(values),
    )