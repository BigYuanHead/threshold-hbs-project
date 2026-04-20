from pathlib import Path


def make_dirs():
    root = Path("benchmark/results")
    raw_dir = root / "raw"
    summary_dir = root / "summary"
    plots_dir = root / "plots"
    raw_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)
    return root, raw_dir, summary_dir, plots_dir