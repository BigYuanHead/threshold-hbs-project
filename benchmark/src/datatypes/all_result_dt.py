from dataclasses import asdict, dataclass
from typing import Any


# >>>>>>>>>>>>>>>>>>> baseline result datatypes >>>>>>>>>>>>>>>>>>>

@dataclass
class BaselineRunResult:
    benchmark_name: str
    total_keys: int
    setup_time: float
    success_rate: float
    avg_signature_size: float
    avg_path_length: float
    sign_time_mean: float
    sign_time_stdev: float
    sign_time_min: float
    sign_time_max: float
    verify_time_mean: float
    verify_time_stdev: float
    verify_time_min: float
    verify_time_max: float
    repeat: int = 0

    def to_dict(self) -> dict:
        return asdict(self)
    

# >>>>>>>>>>>>>>>>>>> baseline threshold datatypes >>>>>>>>>>>>>>>>>>>

@dataclass
class ThresholdRunResult:
    benchmark_name: str
    total_keys: int
    n_parties: int
    setup_time: float

    success_rate: float
    avg_signature_size: float
    avg_path_length: float
    root_size: int

    sign_time_mean: float
    sign_time_stdev: float
    sign_time_min: float
    sign_time_max: float

    verify_time_mean: float
    verify_time_stdev: float
    verify_time_min: float
    verify_time_max: float

    repeat: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

# >>>>>>>>>>>>>>>>>>> batch threshold result datatypes >>>>>>>>>>>>>>>>>>>

@dataclass
class BatchRunResult:
    benchmark_name: str
    total_keys: int
    n_parties: int
    batch_size: int

    batch_sign_time: float
    total_batch_verify_time: float
    per_message_sign_time: float
    per_message_verify_time: float
    batch_pack_size: float
    success_rate: float

    verify_time_mean: float
    verify_time_stdev: float
    verify_time_min: float
    verify_time_max: float

    repeat: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NonBatchRunResult:
    benchmark_name: str
    total_keys: int
    n_parties: int
    message_count: int

    total_sign_time: float
    total_verify_time: float
    per_message_sign_time: float
    per_message_verify_time: float
    total_output_size: float
    success_rate: float

    sign_time_mean: float
    sign_time_stdev: float
    sign_time_min: float
    sign_time_max: float

    verify_time_mean: float
    verify_time_stdev: float
    verify_time_min: float
    verify_time_max: float

    repeat: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BatchFailureResult:
    benchmark_name: str
    total_keys: int
    n_parties: int
    batch_size: int

    verify_correct: bool
    verify_wrong_message_rejected: bool
    verify_wrong_index_rejected: bool
    verify_wrong_path_rejected: bool

    def to_dict(self) -> dict:
        return asdict(self)


# >>>>>>>>>>>>>>>>>>> K of N result datatypes >>>>>>>>>>>>>>>>>>>

@dataclass
class KOfNRunResult:
    benchmark_name: str
    total_keys: int
    n_parties: int
    threshold_k: int
    setup_time: float

    success_rate: float
    avg_signature_size: float

    sign_time_mean: float
    sign_time_stdev: float
    sign_time_min: float
    sign_time_max: float

    verify_time_mean: float
    verify_time_stdev: float
    verify_time_min: float
    verify_time_max: float

    repeat: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class KOfNFailureResult:
    benchmark_name: str
    total_keys: int
    n_parties: int
    threshold_k: int

    verify_correct: bool
    verify_wrong_message_rejected: bool
    less_than_k_rejected: bool
    reuse_key_id_rejected: bool

    def to_dict(self) -> dict:
        return asdict(self)



# >>>>>>>>>>>>>>>>>>> OTS compare result datatypes >>>>>>>>>>>>>>>>>>>

@dataclass
class OtsRunResult:
    benchmark_name: str
    ots_type: str
    total_keys: int
    n_parties: int
    setup_time: float

    success_rate: float
    avg_signature_size: float

    sign_time_mean: float
    sign_time_stdev: float
    sign_time_min: float
    sign_time_max: float

    verify_time_mean: float
    verify_time_stdev: float
    verify_time_min: float
    verify_time_max: float

    repeat: int = 0
    w: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)




@dataclass
class CompareBenchResult:
    rows: list[Any]
    summaries: list[Any]

    def to_dict(self) -> dict:
        return {
            "rows": [row.to_dict() if hasattr(row, "to_dict") else row for row in self.rows],
            "summaries": [summary.to_dict() if hasattr(summary, "to_dict") else summary for summary in self.summaries],
        }