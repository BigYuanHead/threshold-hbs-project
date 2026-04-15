from pathlib import Path

from benchmark.bench_compare import compare_for_n_parties, compare_for_total_keys
from benchmark.metrics import write_csv, write_json


def benchmark_main():
    out_dir = Path("benchmark/results")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Experiment 1: baseline vs threshold as total_keys changes
    total_keys_results = compare_for_total_keys(
        total_keys_list=[4, 8, 16, 32, 64],
        repeats=5,
        n_parties=3,
    )
    write_csv(total_keys_results["rows"], out_dir / "compare_total_keys_rows.csv")
    write_json(total_keys_results["summaries"], out_dir / "compare_total_keys_summary.json")

    # Experiment 2: threshold as number of parties changes
    n_parties_results = compare_for_n_parties(
        total_keys=16,
        n_parties_list=[2, 3, 4],
        repeats=5,
    )
    write_csv(n_parties_results["rows"], out_dir / "compare_n_parties_rows.csv")
    write_json(n_parties_results["summaries"], out_dir / "compare_n_parties_summary.json")

    print("Benchmark completed.")
    print(f"Results written to: {out_dir.resolve()}")


if __name__ == "__main__":
    benchmark_main()