from core.baseline import StatefulHBS
from benchmark.src.utils.metrics import digest32, serialized_size

# dateTypes
from benchmark.src.datatypes.all_cfgs_dt import baselineBench_cfgDt
from benchmark.src.datatypes.all_result_dt import baselineRun_resultDt
from benchmark.src.datatypes.all_summary_dt import baselineBench_sumDt

# timing
from benchmark.src.utils.timer import now, summarize_time_measure



def run_baseline_once(total_keys: int) -> baselineRun_resultDt:
    """
        @ input:
            - total_keys: one time key num in merkle tree
    """

    # baseline system build up
    t0 = now()
    hbs = StatefulHBS(total_keys = total_keys)
    setup_time = now() - t0


    sign_times: list[float] = []
    verify_times: list[float] = []
    signature_sizes: list[int] = []
    path_lengths: list[int] = []
    success_count = 0

    for key_id in range(total_keys):
        # Build one small test message for this key.
        message = digest32(f"baseline-message-{key_id}".encode())

        t1 = now() # sign time
        signed_data = hbs.sign(key_id, message)
        sign_times.append(now() - t1)

        signature_sizes.append(serialized_size(signed_data))
        path_lengths.append(len(signed_data["path"]))
        
        t2 = now() # verify time
        ok = hbs.verify(message, signed_data)
        verify_times.append(now() - t2)

        if ok:
            success_count += 1

    sign_stats = summarize_time_measure(sign_times)
    verify_stats = summarize_time_measure(verify_times)

    return baselineRun_resultDt(
        benchmark_name = "baseline",
        total_keys = total_keys,
        setup_time = setup_time,
        success_rate = success_count / total_keys,
        avg_signature_size = sum(signature_sizes) / len(signature_sizes),
        avg_path_length = sum(path_lengths) / len(path_lengths),

        sign_time_mean = sign_stats.mean,
        sign_time_stdev = sign_stats.stdev,
        sign_time_min = sign_stats.min_value,
        sign_time_max = sign_stats.max_value,

        verify_time_mean = verify_stats.mean,
        verify_time_stdev = verify_stats.stdev,
        verify_time_min = verify_stats.min_value,
        verify_time_max = verify_stats.max_value,
    )



def benchmark_baseline(total_keys: int,
                       repeats: int = 5) -> tuple[list[baselineRun_resultDt],
                                                  baselineBench_sumDt]:
    """
        Run the baseline benchmark multiple times.
    """

    CONFIG = baselineBench_cfgDt(total_keys = total_keys,
                                 repeats = repeats)
    rows: list[baselineRun_resultDt] = []

    # repeat run
    for repeat in range(CONFIG.repeats):
        row = run_baseline_once(total_keys = CONFIG.total_keys)
        row.repeat = repeat
        rows.append(row)

    summary = baselineBench_sumDt(
        benchmark_name = "baseline",
        total_keys = CONFIG.total_keys,
        repeats = CONFIG.repeats,
        setup_time_mean = sum(row.setup_time for row in rows) / CONFIG.repeats,
        success_rate_mean = sum(row.success_rate for row in rows) / CONFIG.repeats,
        avg_signature_size_mean = sum(row.avg_signature_size for row in rows) / CONFIG.repeats,
        avg_path_length_mean = sum(row.avg_path_length for row in rows) / CONFIG.repeats,
        sign_time_mean_mean = sum(row.sign_time_mean for row in rows) / CONFIG.repeats,
        verify_time_mean_mean = sum(row.verify_time_mean for row in rows) / CONFIG.repeats,
    )

    return rows, summary