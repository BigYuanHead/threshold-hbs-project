from dataclasses import asdict, dataclass



# >>>>>>>>>>>>>> baseline configs >>>>>>>>>>>>>>

@dataclass
class BaselineBenchConfig:
    total_keys: int
    repeats: int = 5

# >>>>>>>>>>>>>> batch configs >>>>>>>>>>>>>>

@dataclass
class BatchBenchConfig:
    total_keys: int
    n_parties: int
    batch_size: int
    repeats: int = 5
    key_id: int = 0


# >>>>>>>>>>>>>> K of N configs >>>>>>>>>>>>>>

@dataclass
class KOfNBenchConfig:
    total_keys: int
    n_parties: int
    threshold_k: int
    repeats: int = 5


# >>>>>>>>>>>>>> OTS compare configs >>>>>>>>>>>>>>
@dataclass
class OtsCompareConfig:
    total_keys: int
    n_parties: int
    repeats: int = 5
    w: int = 16



# >>>>>>>>>>>>>> compare configs >>>>>>>>>>>>>>

@dataclass
class KOfNCompareConfig:
    total_keys: int
    n_parties: int
    k_values: list[int]
    repeats: int = 5





@dataclass
class CompareTotalKeysConfig:
    total_keys_list: list[int]
    repeats: int = 5
    n_parties: int = 3

@dataclass
class CompareNPartiesConfig:
    total_keys: int
    n_parties_list: list[int]
    repeats: int = 5