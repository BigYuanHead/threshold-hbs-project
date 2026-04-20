import time
from contextlib import contextmanager


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