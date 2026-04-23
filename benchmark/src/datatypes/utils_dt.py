from dataclasses import asdict, dataclass


@dataclass
class TimeStats:
    mean: float
    stdev: float
    min_value: float
    max_value: float