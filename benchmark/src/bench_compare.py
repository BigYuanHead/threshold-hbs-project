from benchmark.src.bench_baseline import benchmark_baseline
from benchmark.src.bench_threshold import benchmark_threshold


def compare_for_total_keys(total_keys_list: list[int], repeats: int = 5, n_parties: int = 3) -> dict:
    all_rows = []
    summaries = []

    for total_keys in total_keys_list:
        baseline_rows, baseline_summary = benchmark_baseline(
            total_keys=total_keys,
            repeats=repeats,
        )
        threshold_rows, threshold_summary = benchmark_threshold(
            total_keys=total_keys,
            n_parties=n_parties,
            repeats=repeats,
        )

        all_rows.extend(baseline_rows)
        all_rows.extend(threshold_rows)
        summaries.append(baseline_summary)
        summaries.append(threshold_summary)

    return {
        "rows": all_rows,
        "summaries": summaries,
    }


def compare_for_n_parties(total_keys: int, n_parties_list: list[int], repeats: int = 5) -> dict:
    all_rows = []
    summaries = []

    for n_parties in n_parties_list:
        threshold_rows, threshold_summary = benchmark_threshold(
            total_keys=total_keys,
            n_parties=n_parties,
            repeats=repeats,
        )
        all_rows.extend(threshold_rows)
        summaries.append(threshold_summary)

    return {
        "rows": all_rows,
        "summaries": summaries,
    }