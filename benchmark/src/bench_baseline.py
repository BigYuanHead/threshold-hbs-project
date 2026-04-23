import time
from dataclasses import asdict, dataclass

from core.baseline import StatefulHBS
from benchmark.src.utils.metrics import digest32, serialized_size



from benchmark.src.datatypes.all_cfgs_dt import BaselineBenchConfig
from benchmark.src.datatypes.all_result_dt import BaselineRunResult
from benchmark.src.datatypes.all_summary_dt import BaselineBenchSummary

# timing
from benchmark.src.datatypes.utils_dt import TimeStats
from benchmark.src.utils.timer import now, timed, summarize_time_measure






def run_baseline_once(total_keys: int) -> BaselineRunResult:
    """
        Run the baseline HBS once.

        @ input:
            - total_keys: onetime key number in the merkle tree

        @ return:
            ...
    """

    t0 = now()
    hbs = StatefulHBS(total_keys = total_keys) #init
    setup_time = now() - t0

    # collect output from algo
    sign_times: list[float] = []
    verify_times: list[float] = []
    signature_sizes: list[int] = []
    path_lengths: list[int] = []
    success_count = 0

    for key_id in range(total_keys):

        # fake msg
        message = digest32(f"baseline-message-{key_id}".encode())

        t1 = now()
        signed_data = hbs.sign(key_id, message) # hbs sign
        sign_times.append(now() - t1)

        signature_sizes.append(serialized_size(signed_data))
        path_lengths.append(len(signed_data["path"]))

        t2 = now()
        ok = hbs.verify(message, signed_data) # hbs verify
        verify_times.append(now() - t2)
        
        if ok:
            success_count += 1

    sign_stats = summarize_time_measure(sign_times)
    verify_stats = summarize_time_measure(verify_times)

    return BaselineRunResult(
        benchmark_name = "baseline",
        total_keys = total_keys,
        setup_time = setup_time,

        success_rate = success_count / total_keys,
        avg_signature_size = sum(signature_sizes) / len(signature_sizes),
        avg_path_length = sum(path_lengths) / len(path_lengths),

        # sign time
        sign_time_mean = sign_stats.mean,
        sign_time_stdev = sign_stats.stdev,
        sign_time_min = sign_stats.min_value,
        sign_time_max = sign_stats.max_value,
        # verify time
        verify_time_mean = verify_stats.mean,
        verify_time_stdev = verify_stats.stdev,
        verify_time_min = verify_stats.min_value,
        verify_time_max = verify_stats.max_value,
    )


def benchmark_baseline(total_keys: int,
                       repeats: int = 5) -> tuple[list[BaselineRunResult],
                                                  BaselineBenchSummary]:
    """
        run multi times
    """
    config = BaselineBenchConfig(total_keys = total_keys, repeats = repeats)
    rows: list[BaselineRunResult] = []

    for repeat in range(config.repeats):
        row = run_baseline_once(total_keys=config.total_keys)
        row.repeat = repeat
        rows.append(row)

    summary = BaselineBenchSummary(
        benchmark_name = "baseline",
        total_keys = config.total_keys,
        repeats = config.repeats,
        setup_time_mean = sum(row.setup_time for row in rows) / config.repeats,
        success_rate_mean = sum(row.success_rate for row in rows) / config.repeats,
        avg_signature_size_mean = sum(row.avg_signature_size for row in rows) / config.repeats,
        avg_path_length_mean = sum(row.avg_path_length for row in rows) / config.repeats,
        sign_time_mean_mean = sum(row.sign_time_mean for row in rows) / config.repeats,
        verify_time_mean_mean = sum(row.verify_time_mean for row in rows) / config.repeats,
    )
    return rows, summary