from dataclasses import asdict, dataclass


@dataclass
class timeStats:
    mean: float
    stdev: float
    min_value: float
    max_value: float