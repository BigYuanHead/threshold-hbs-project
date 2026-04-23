from dataclasses import asdict, dataclass
from typing import Any

from benchmark.src.bench_baseline import benchmark_baseline
from benchmark.src.bench_threshold import benchmark_threshold



from benchmark.src.datatypes.all_cfgs_dt import compareNParties_cfgDt, compareTotalKeys_cfgDt
from benchmark.src.datatypes.all_result_dt import compareBench_resultDT



def compare_for_total_keys(total_keys_list: list[int],
                           repeats: int = 5,
                           n_parties: int = 3) -> compareBench_resultDT:
    """
        compare baseline and threshold only change total_keys
    """
    config = compareTotalKeys_cfgDt(total_keys_list = total_keys_list,
                                    repeats = repeats,
                                    n_parties = n_parties)

    all_rows = []
    summaries = []

    for total_keys in config.total_keys_list:
        baseline_rows, baseline_summary = benchmark_baseline(
            total_keys = total_keys,
            repeats = config.repeats,
        )
        threshold_rows, threshold_summary = benchmark_threshold(
            total_keys = total_keys,
            n_parties = config.n_parties,
            repeats = config.repeats,
        )

        all_rows.extend(baseline_rows)
        all_rows.extend(threshold_rows)
        summaries.append(baseline_summary)
        summaries.append(threshold_summary)

    return compareBench_resultDT(rows = all_rows,
                                 summaries = summaries)



def compare_for_n_parties(total_keys: int,
                          n_parties_list: list[int],
                          repeats: int = 5) -> compareBench_resultDT:
    """
        Compare threshold benchmarks while only changing n_parties.

        @ input:
            - total_keys: fixed one-time key number
            - n_parties_list: values to test
            - repeats: repeat count for each setting

        @ return:
            - raw rows and summaries for all settings
    """
    config = compareNParties_cfgDt(total_keys = total_keys,
                                   n_parties_list = n_parties_list,
                                   repeats = repeats)

    all_rows = []
    summaries = []

    for n_parties in config.n_parties_list:
        threshold_rows, threshold_summary = benchmark_threshold(
            total_keys = config.total_keys,
            n_parties = n_parties,
            repeats = config.repeats,
        )
        all_rows.extend(threshold_rows)
        summaries.append(threshold_summary)

    return compareBench_resultDT(rows = all_rows,
                                 summaries = summaries)