from dataclasses import asdict, dataclass



# >>>>>>>>>>>>>> baseline configs >>>>>>>>>>>>>>

@dataclass
class baselineBench_cfgDt:
    total_keys: int
    repeats: int = 5

# >>>>>>>>>>>>>> batch configs >>>>>>>>>>>>>>

@dataclass
class batchBench_cfgDt:
    total_keys: int
    n_parties: int
    batch_size: int
    repeats: int = 5
    key_id: int = 0


# >>>>>>>>>>>>>> K of N configs >>>>>>>>>>>>>>

@dataclass
class KOfNBench_cfgDt:
    total_keys: int
    n_parties: int
    threshold_k: int
    repeats: int = 5


# >>>>>>>>>>>>>> OTS compare configs >>>>>>>>>>>>>>
@dataclass
class otsCompare_cfgDt:
    total_keys: int
    n_parties: int
    repeats: int = 5
    w: int = 16

@dataclass
class winternitzSweep_cfgDt:
    total_keys: int
    n_parties: int
    w_values: list[int]
    repeats: int = 5


# >>>>>>>>>>>> threshold compare configs >>>>>>>>>>>>>>
@dataclass
class thresholdBench_cfgDt:
    total_keys: int
    n_parties: int
    repeats: int = 5




# >>>>>>>>>>>>>> compare configs >>>>>>>>>>>>>>

@dataclass
class KOfNCompare_cfgDt:
    total_keys: int
    n_parties: int
    k_values: list[int]
    repeats: int = 5


@dataclass
class compareTotalKeys_cfgDt:
    total_keys_list: list[int]
    repeats: int = 5
    n_parties: int = 3


@dataclass
class compareNParties_cfgDt:
    total_keys: int
    n_parties_list: list[int]
    repeats: int = 5