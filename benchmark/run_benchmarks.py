from pathlib import Path
import os
import sys

sys.path.append(os.path.abspath("."))

from benchmark.src.utils import utils
from benchmark.src.utils.metrics import (
    write_csv,
    write_json,
    save_summary,
    plot_multiLine_subplots,
    plot_multiBar_subplots,
    build_relative_overhead_df,
)

from benchmark.src.bench_compare import compare_for_n_parties, compare_for_total_keys
from benchmark.src.bench_kofn import benchmark_kofn_by_k, benchmark_kofn_failures
from benchmark.src.bench_batch_threshold import (
    benchmark_batch_by_size,
    compare_batch_vs_nonbatch,
    benchmark_batch_failures,
)
from benchmark.src.bench_ots_compare import (
    benchmark_lamport_vs_winternitz,
    benchmark_winternitz_by_w,
)


# This file runs all benchmark experiments and saves raw results, summaries, and plots.
CONFIG = {
    "repeats_main": 7,
    "repeats_ext": 5,

    # Exp A: total_keys scaling
    "total_keys_values": [4, 8, 16, 32, 64, 128],
    "total_keys_fixed_n_parties": 3,

    # Exp B: n_parties scaling
    "n_parties_values": [2, 3, 4, 5],
    "n_parties_fixed_total_keys": 32,

    # Exp C: k-of-n scaling
    "kofn_total_keys": 16,
    "kofn_n_parties": 4,
    "kofn_k_values": [2, 3, 4],

    # Exp D: batch scaling
    "batch_total_keys": 32,
    "batch_n_parties": 3,
    "batch_sizes": [2, 4, 8, 16, 32],
    "batch_vs_nonbatch_message_count": 16,

    # Exp E: Lamport vs Winternitz
    "ots_total_keys": 16,
    "ots_n_parties": 3,
    "ots_w": 16,
    "ots_w_values": [4, 8, 16],
}


def print_benchmark_overview(raw_dir: Path, summary_dir: Path, plots_dir: Path) -> None:
    print("\n" + ">>" * 20 + " Start running experiments " + ">>" * 20)
    print("Benchmark configuration loaded.")
    print(f"Main experiment repeats: {CONFIG['repeats_main']}")
    print(f"Extension experiment repeats: {CONFIG['repeats_ext']}")
    print("\nPlanned experiment groups:")
    print("  [1/6] Baseline vs threshold over total_keys")
    print("  [2/6] Threshold scaling with n_parties")
    print("  [3/6] k-of-n scaling with threshold_k")
    print("  [4/6] Batch signing evaluation")
    print("  [5/6] Lamport vs Winternitz comparison")
    print("  [6/6] Winternitz scaling with w")
    print(f"\nRaw results directory:\n{raw_dir.resolve()}")
    print(f"\nSummary results directory:\n{summary_dir.resolve()}")
    print(f"\nPlots directory:\n{plots_dir.resolve()}")


def print_stage_start(stage_no: int, title: str, description: str) -> None:
    print(f"\n[{stage_no}/6] {title}")
    print(f"  {description}")


def print_stage_done(
    stage_no: int,
    raw_paths: list[Path],
    summary_paths: list[Path],
    plot_paths: list[Path],
) -> None:
    print(f"[{stage_no}/6] Completed")
    if raw_paths:
        print("  Raw output:")
        for path in raw_paths:
            print(f"    - {path.resolve()}")
    if summary_paths:
        print("  Summary output:")
        for path in summary_paths:
            print(f"    - {path.resolve()}")
    if plot_paths:
        print("  Plot output:")
        for path in plot_paths:
            print(f"    - {path.resolve()}")


 # >>>>>>>>>>>>>>>>> init all dir >>>>>>>>>>>>>>>>>
_, RAW_DIR, SUMMARY_DIR, PLOTS_DIR = utils.make_dirs()


def expName2files(exp_name: str, suffix: str = None) -> tuple[Path, Path, Path]:
    """
        Build the default raw / summary / json file paths for one experiment.
    """
    RAW_PATH = RAW_DIR / "{}_raw.csv".format(exp_name)
    SUMMARY_PATH = SUMMARY_DIR / "{}_summary.csv".format(exp_name)
    JSON_PATH = SUMMARY_DIR / "{}_summary.json".format(exp_name)
    if suffix:
        JSON_PATH = SUMMARY_DIR / "{}_{}_summary.json".format(exp_name, suffix)
    return RAW_PATH, SUMMARY_PATH, JSON_PATH



def runExp_totalKeys():
    """
        change total_keys
    """

    EXP_NAME = "total_keys_scaling"

    RAW_PATH, SUMMARY_PATH, JSON_PATH = expName2files(EXP_NAME)
    RELATIVE_SUMMARY_PATH = SUMMARY_DIR / "{}_relative_summary.csv".format(EXP_NAME)

    # run
    compare_result = compare_for_total_keys(
        total_keys_list = CONFIG["total_keys_values"],
        repeats = CONFIG["repeats_main"],
        n_parties = CONFIG["total_keys_fixed_n_parties"],
    )
    rows = compare_result.rows
    summaries = compare_result.summaries

    write_csv(rows, RAW_PATH)
    write_json(summaries, JSON_PATH)

    # x: n_parties; y: setup_time, sign_time_mean, verify_time_mean, avg_signature_size
    summary_df = save_summary(
        rows = rows,
        groupby_cols = ["benchmark_name", "total_keys"],
        metric_cols = ["setup_time", "sign_time_mean", "verify_time_mean", "avg_signature_size"],
        output_path = SUMMARY_PATH,
    )

    relative_df = build_relative_overhead_df(summary_df)
    if not relative_df.empty:
        relative_df.to_csv(RELATIVE_SUMMARY_PATH, index = False)

    # plot
    plot_multiLine_subplots(
        summary_df = summary_df,
        x_col = "total_keys",
        group_col = "benchmark_name",
        metrics = [
            ("setup_time_mean", "Setup Time (s)", "setup_time_std"),
            ("sign_time_mean_mean", "Sign Time (s)", "sign_time_mean_std"),
            ("verify_time_mean_mean", "Verify Time (s)", "verify_time_mean_std"),
            ("avg_signature_size_mean", "Signature Size (bytes)", "avg_signature_size_std"),
        ],
        layout = (2, 2),
        title = "Scaling with total_keys",
        output_path = PLOTS_DIR / "exp_total_keys_2x2.png",
    )

    plot_multiLine_subplots(
        summary_df = relative_df,
        x_col = "total_keys",
        group_col = None,
        metrics = [
            ("setup_time_ratio", "Setup Overhead (threshold / baseline)", None),
            ("sign_time_ratio", "Sign Overhead (threshold / baseline)", None),
            ("verify_time_ratio", "Verify Overhead (threshold / baseline)", None),
            ("signature_size_ratio", "Signature Size Overhead (threshold / baseline)", None),
        ],
        layout = (2, 2),
        title = "Relative Overhead with total_keys",
        output_path = PLOTS_DIR / "exp_total_keys_relative_2x2.png",
    )



def runExp_nParties():
    """
        only changing n_parties
    """

    EXP_NAME = "exp_n_parties"
    RAW_PATH, SUMMARY_PATH, JSON_PATH = expName2files(EXP_NAME)

    # run 
    compare_result = compare_for_n_parties(
        total_keys = CONFIG["n_parties_fixed_total_keys"],
        n_parties_list = CONFIG["n_parties_values"],
        repeats = CONFIG["repeats_main"],
    )
    rows = compare_result.rows
    summaries = compare_result.summaries

    write_csv(rows, RAW_PATH)
    write_json(summaries, JSON_PATH)

    # x: n_parties; y: setup_time, sign_time_mean, verify_time_mean, avg_signature_size
    summary_df = save_summary(
        rows = rows,
        groupby_cols = ["n_parties"],
        metric_cols = ["setup_time", "sign_time_mean", "verify_time_mean", "avg_signature_size"],
        output_path = SUMMARY_PATH,
    )

    # x: n_parties; y: setup_time, sign_time_mean, verify_time_mean
    plot_multiLine_subplots(
        summary_df = summary_df,
        x_col = "n_parties",
        group_col = None,
        metrics = [
            ("setup_time_mean", "Setup Time (s)", "setup_time_std"),
            ("sign_time_mean_mean", "Sign Time (s)", "sign_time_mean_std"),
            ("verify_time_mean_mean", "Verify Time (s)", "verify_time_mean_std"),
        ],
        layout = (1, 3),
        title = "Threshold Scaling with n_parties",
        output_path = PLOTS_DIR / "exp_n_parties_1x3.png",
    )



def runExp_kofn():
    """
        change k in k-of-n
    """

    EXP_NAME = "exp_kofn"
    RAW_PATH, SUMMARY_PATH, JSON_PATH = expName2files(EXP_NAME,
                                                      suffix="failures")

    rows = benchmark_kofn_by_k(
        total_keys = CONFIG["kofn_total_keys"],
        n_parties = CONFIG["kofn_n_parties"],
        k_values = CONFIG["kofn_k_values"],
        repeats = CONFIG["repeats_ext"],
    )
    failure_result = benchmark_kofn_failures(
        total_keys = 8,
        n_parties = CONFIG["kofn_n_parties"],
        threshold_k = 3,
    )

    write_csv(rows, RAW_PATH)
    write_json(failure_result, JSON_PATH)

    summary_df = save_summary(
        rows = rows,
        groupby_cols = ["threshold_k"],
        metric_cols = ["setup_time", "sign_time_mean", "verify_time_mean", "avg_signature_size"],
        output_path = SUMMARY_PATH,
    )

    plot_multiLine_subplots(
        summary_df = summary_df,
        x_col = "threshold_k",
        group_col = None,
        metrics = [
            ("sign_time_mean_mean", "Sign Time (s)", "sign_time_mean_std"),
            ("verify_time_mean_mean", "Verify Time (s)", "verify_time_mean_std"),
            ("avg_signature_size_mean", "Signature Size (bytes)", "avg_signature_size_std"),
        ],
        layout = (1, 3),
        title = "k-of-n Scaling with k",
        output_path = PLOTS_DIR / "exp_kofn_1x3.png",
    )



def runExp_batch():
    """
        batch-size scale and batch vs nonbatch
    """

    EXP_NAME = "exp_batch_scaling"
    RAW_PATH, SUMMARY_PATH, JSON_PATH = expName2files(EXP_NAME,
                                                      suffix="failures")
    
    EXP_COMPARE_NAME = "exp_batch_vs_nonbatch"
    COMPARE_RAW_PATH, COMPARE_SUMMARY_PATH, _ = expName2files(EXP_COMPARE_NAME)

    batch_rows = benchmark_batch_by_size(
        total_keys = CONFIG["batch_total_keys"],
        n_parties = CONFIG["batch_n_parties"],
        batch_sizes = CONFIG["batch_sizes"],
        repeats = CONFIG["repeats_ext"],
    )
    batch_vs_nonbatch_rows = compare_batch_vs_nonbatch(
        total_keys = CONFIG["batch_total_keys"],
        n_parties = CONFIG["batch_n_parties"],
        message_count = CONFIG["batch_vs_nonbatch_message_count"],
        repeats = CONFIG["repeats_ext"],
    )
    batch_failure_result = benchmark_batch_failures(
        total_keys = 16,
        n_parties = CONFIG["batch_n_parties"],
        batch_size = 8,
    )

    write_csv(batch_rows, RAW_PATH)
    write_csv(batch_vs_nonbatch_rows, COMPARE_RAW_PATH)
    write_json(batch_failure_result, JSON_PATH)

    summary_df = save_summary(
        rows = batch_rows,
        groupby_cols = ["batch_size"],
        metric_cols = [
            "batch_sign_time",
            "total_batch_verify_time",
            "per_message_sign_time",
            "per_message_verify_time",
            "batch_pack_size",
        ],
        output_path = SUMMARY_PATH,
    )

    save_summary(
        rows = batch_vs_nonbatch_rows,
        groupby_cols = ["benchmark_name"],
        metric_cols = [
            "total_sign_time",
            "total_verify_time",
            "per_message_sign_time",
            "per_message_verify_time",
            "total_output_size",
            "batch_sign_time",
            "total_batch_verify_time",
            "batch_pack_size",
        ],
        output_path = COMPARE_SUMMARY_PATH,
    )

    plot_multiLine_subplots(
        summary_df = summary_df,
        x_col = "batch_size",
        group_col = None,
        metrics = [
            ("batch_sign_time_mean", "Total Batch Sign Time (s)", "batch_sign_time_std"),
            ("per_message_sign_time_mean", "Per-message Sign Time (s)", "per_message_sign_time_std"),
            ("total_batch_verify_time_mean", "Total Batch Verify Time (s)", "total_batch_verify_time_std"),
            ("per_message_verify_time_mean", "Per-message Verify Time (s)", "per_message_verify_time_std"),
        ],
        layout = (2, 2),
        title = "Batch Scaling with batch_size",
        output_path = PLOTS_DIR / "exp_batch_2x2.png",
    )



def runExp_ots():
    """
        lamport vs winternitz
    """

    EXP_NAME = "exp_lamport_vs_winternitz"
    RAW_PATH, SUMMARY_PATH, JSON_PATH = expName2files(EXP_NAME)

    # Compare Lamport and Winternitz under one fixed w.
    rows, summaries = benchmark_lamport_vs_winternitz(
        total_keys = CONFIG["ots_total_keys"],
        n_parties = CONFIG["ots_n_parties"],
        w = CONFIG["ots_w"],
        repeats = CONFIG["repeats_ext"],
    )

    write_csv(rows, RAW_PATH)
    write_json(summaries, JSON_PATH)

    summary_df = save_summary(
        rows = rows,
        groupby_cols = ["ots_type"],
        metric_cols = ["setup_time", "sign_time_mean", "verify_time_mean", "avg_signature_size"],
        output_path = SUMMARY_PATH,
    )

    plot_multiBar_subplots(
        summary_df = summary_df,
        x_col = "ots_type",
        metrics = [
            ("setup_time_mean", "Setup Time (s)"),
            ("sign_time_mean_mean", "Sign Time (s)"),
            ("verify_time_mean_mean", "Verify Time (s)"),
            ("avg_signature_size_mean", "Signature Size (bytes)"),
        ],
        layout = (2, 2),
        title = "Lamport vs Winternitz",
        output_path = PLOTS_DIR / "exp_ots_2x2.png",
    )



def runExp_winternitzW():
    """
       change w for winternitz
    """
    EXP_NAME = "exp_winternitz_by_w"
    RAW_PATH, SUMMARY_PATH, JSON_PATH = expName2files(EXP_NAME)

    rows, summaries = benchmark_winternitz_by_w(
        total_keys = CONFIG["ots_total_keys"],
        n_parties = CONFIG["ots_n_parties"],
        w_values = CONFIG["ots_w_values"],
        repeats = CONFIG["repeats_ext"],
    )

    write_csv(rows, RAW_PATH)
    write_json(summaries, JSON_PATH)

    summary_df = save_summary(
        rows = rows,
        groupby_cols = ["w"],
        metric_cols = ["setup_time", "sign_time_mean", "verify_time_mean", "avg_signature_size"],
        output_path = SUMMARY_PATH,
    )

    plot_multiLine_subplots(
        summary_df = summary_df,
        x_col = "w",
        group_col = None,
        metrics = [
            ("setup_time_mean", "Setup Time (s)", "setup_time_std"),
            ("sign_time_mean_mean", "Sign Time (s)", "sign_time_mean_std"),
            ("verify_time_mean_mean", "Verify Time (s)", "verify_time_mean_std"),
            ("avg_signature_size_mean", "Signature Size (bytes)", "avg_signature_size_std"),
        ],
        layout = (2, 2),
        title = "Winternitz Scaling with w",
        output_path = PLOTS_DIR / "exp_winternitz_by_w_2x2.png",
    )



def benchmark_main():
    
    # save exp config 
    write_json(CONFIG, SUMMARY_DIR / "benchmark_config.json")

    print_benchmark_overview(RAW_DIR, SUMMARY_DIR, PLOTS_DIR)

    print_stage_start(
        1,
        "Baseline vs threshold over total_keys",
        "Variable: total_keys | Fixed: n_parties = 3",
    )
    runExp_totalKeys()
    print_stage_done(
        1,
        [RAW_DIR / "exp_total_keys_raw.csv"],
        [
            SUMMARY_DIR / "exp_total_keys_summary.csv",
            SUMMARY_DIR / "exp_total_keys_summary.json",
        ],
        [PLOTS_DIR / "exp_total_keys_2x2.png"],
    )

    print_stage_start(
        2,
        "Threshold scaling with n_parties",
        "Variable: n_parties | Fixed: total_keys = 32",
    )
    runExp_nParties()
    print_stage_done(
        2,
        [RAW_DIR / "exp_n_parties_raw.csv"],
        [
            SUMMARY_DIR / "exp_n_parties_summary.csv",
            SUMMARY_DIR / "exp_n_parties_summary.json",
        ],
        [PLOTS_DIR / "exp_n_parties_1x3.png"],
    )

    print_stage_start(
        3,
        "k-of-n scaling",
        "Variable: threshold_k | Fixed: n_parties = 4, total_keys = 16",
    )
    runExp_kofn()
    print_stage_done(
        3,
        [RAW_DIR / "exp_kofn_raw.csv"],
        [
            SUMMARY_DIR / "exp_kofn_summary.csv",
            SUMMARY_DIR / "exp_kofn_failures.json",
        ],
        [PLOTS_DIR / "exp_kofn_1x3.png"],
    )

    print_stage_start(
        4,
        "Batch signing evaluation",
        "Variable: batch_size | Fixed: total_keys = 32, n_parties = 3",
    )
    runExp_batch()
    print_stage_done(
        4,
        [
            RAW_DIR / "exp_batch_scaling_raw.csv",
            RAW_DIR / "exp_batch_vs_nonbatch_raw.csv",
        ],
        [
            SUMMARY_DIR / "exp_batch_scaling_summary.csv",
            SUMMARY_DIR / "exp_batch_vs_nonbatch_summary.csv",
            SUMMARY_DIR / "exp_batch_failures.json",
        ],
        [PLOTS_DIR / "exp_batch_2x2.png"],
    )

    print_stage_start(
        5,
        "Lamport vs Winternitz comparison",
        "Variable: OTS type | Fixed: total_keys = 16, n_parties = 3, w = 16",
    )
    runExp_ots()
    print_stage_done(
        5,
        [RAW_DIR / "exp_lamport_vs_winternitz_raw.csv"],
        [
            SUMMARY_DIR / "exp_lamport_vs_winternitz_summary.csv",
            SUMMARY_DIR / "exp_lamport_vs_winternitz_summary.json",
        ],
        [PLOTS_DIR / "exp_ots_2x2.png"],
    )

    print_stage_start(
        6,
        "Winternitz scaling with w",
        "Variable: w | Fixed: total_keys = 16, n_parties = 3",
    )
    runExp_winternitzW()
    print_stage_done(
        6,
        [RAW_DIR / "exp_winternitz_by_w_raw.csv"],
        [
            SUMMARY_DIR / "exp_winternitz_by_w_summary.csv",
            SUMMARY_DIR / "exp_winternitz_by_w_summary.json",
        ],
        [PLOTS_DIR / "exp_winternitz_by_w_2x2.png"],
    )

    print("\n" + "<<" * 20 + " Benchmark completed " + "<<" * 20)
    print(f"\nRaw results:\n{RAW_DIR.resolve()}")
    print(f"\nSummary results:\n{SUMMARY_DIR.resolve()}")
    print(f"\nPlots:\n{PLOTS_DIR.resolve()}")


if __name__ == "__main__":
    benchmark_main()
