from dataclasses import asdict, dataclass


@dataclass
class BaselineBenchSummary:
    benchmark_name: str
    total_keys: int
    repeats: int
    setup_time_mean: float
    success_rate_mean: float
    avg_signature_size_mean: float
    avg_path_length_mean: float
    sign_time_mean_mean: float
    verify_time_mean_mean: float

    def to_dict(self) -> dict:
        return asdict(self)
    


@dataclass
class KOfNBenchSummary:
    benchmark_name: str
    total_keys: int
    n_parties: int
    threshold_k: int
    repeats: int

    setup_time_mean: float
    success_rate_mean: float
    avg_signature_size_mean: float
    sign_time_mean_mean: float
    verify_time_mean_mean: float

    def to_dict(self) -> dict:
        return asdict(self)
    



@dataclass
class OtsBenchSummary:
    benchmark_name: str
    ots_type: str
    total_keys: int
    n_parties: int
    repeats: int
    w: int | None = None

    setup_time_mean: float = 0.0
    success_rate_mean: float = 0.0
    avg_signature_size_mean: float = 0.0
    sign_time_mean_mean: float = 0.0
    verify_time_mean_mean: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)