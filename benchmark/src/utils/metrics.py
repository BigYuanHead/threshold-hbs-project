from pathlib import Path
import csv
import json
import hashlib
import pickle
import statistics
from typing import Iterable

import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# basic helpers
# -----------------------------
def digest32(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def serialized_size(obj) -> int:
    return len(pickle.dumps(obj))


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.mean(values) if values else 0.0


def stdev(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def summarise_times(values: list[float], prefix: str) -> dict:
    return {
        f"{prefix}_mean": mean(values),
        f"{prefix}_stdev": stdev(values),
        f"{prefix}_min": min(values) if values else 0.0,
        f"{prefix}_max": max(values) if values else 0.0,
    }


# -----------------------------
# file writing
# -----------------------------
def write_csv(rows: list[dict], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("")
        return

    fieldnames = sorted({key for row in rows for key in row.keys()})
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(obj, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


# -----------------------------
# dataframe + aggregation
# -----------------------------
def rows_to_df(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def save_summary(
    rows: list[dict],
    groupby_cols: list[str],
    metric_cols: list[str],
    output_path: str | Path,
) -> pd.DataFrame:
    """
    Group raw rows by groupby_cols and compute mean/std for metric_cols.
    """
    df = rows_to_df(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        df.to_csv(output_path, index=False)
        return df

    agg_map = {col: ["mean", "std"] for col in metric_cols if col in df.columns}
    summary = df.groupby(groupby_cols, dropna=False).agg(agg_map).reset_index()

    # flatten multi-index columns
    flat_cols = []
    for col in summary.columns:
        if isinstance(col, tuple):
            left, right = col
            if right == "":
                flat_cols.append(left)
            else:
                flat_cols.append(f"{left}_{right}")
        else:
            flat_cols.append(col)
    summary.columns = flat_cols

    summary.to_csv(output_path, index=False)
    return summary


# -----------------------------
# plotting helpers
# -----------------------------
def ensure_plot_dir(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def plot_line_from_summary(
    summary_df: pd.DataFrame,
    x_col: str,
    y_mean_col: str,
    y_std_col: str | None,
    group_col: str | None,
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: str | Path,
) -> None:
    output_path = ensure_plot_dir(output_path)
    plt.figure(figsize=(8, 5))

    if summary_df.empty:
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    if group_col and group_col in summary_df.columns:
        for group_value, group_df in summary_df.groupby(group_col):
            group_df = group_df.sort_values(by=x_col)
            plt.plot(group_df[x_col], group_df[y_mean_col], marker="o", label=str(group_value))
            if y_std_col and y_std_col in group_df.columns:
                lower = group_df[y_mean_col] - group_df[y_std_col].fillna(0)
                upper = group_df[y_mean_col] + group_df[y_std_col].fillna(0)
                plt.fill_between(group_df[x_col], lower, upper, alpha=0.15)
        plt.legend()
    else:
        summary_df = summary_df.sort_values(by=x_col)
        plt.plot(summary_df[x_col], summary_df[y_mean_col], marker="o")
        if y_std_col and y_std_col in summary_df.columns:
            lower = summary_df[y_mean_col] - summary_df[y_std_col].fillna(0)
            upper = summary_df[y_mean_col] + summary_df[y_std_col].fillna(0)
            plt.fill_between(summary_df[x_col], lower, upper, alpha=0.15)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_grouped_bar_from_summary(
    summary_df: pd.DataFrame,
    x_col: str,
    y_mean_col: str,
    group_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: str | Path,
) -> None:
    output_path = ensure_plot_dir(output_path)
    plt.figure(figsize=(9, 5))

    if summary_df.empty:
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    pivot_df = summary_df.pivot(index=x_col, columns=group_col, values=y_mean_col)
    pivot_df.plot(kind="bar", ax=plt.gca())

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_overall_comparison(
    rows: list[dict],
    scheme_col: str,
    metric_cols: list[str],
    output_path: str | Path,
    title: str = "Overall Comparison",
) -> None:
    output_path = ensure_plot_dir(output_path)
    df = rows_to_df(rows)

    if df.empty:
        plt.figure(figsize=(8, 5))
        plt.title(title)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    usable_metrics = [m for m in metric_cols if m in df.columns]
    if not usable_metrics:
        plt.figure(figsize=(8, 5))
        plt.title(title)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    summary = df.groupby(scheme_col)[usable_metrics].mean().reset_index()
    summary = summary.set_index(scheme_col)

    plt.figure(figsize=(10, 5))
    summary.plot(kind="bar", ax=plt.gca())
    plt.title(title)
    plt.xlabel("Scheme")
    plt.ylabel("Average value")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()



def plot_ots_comparison_2x2(
    summary_df,
    x_col: str,
    output_path,
    title: str = "Lamport vs Winternitz Comparison",
):
    output_path = ensure_plot_dir(output_path)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    if summary_df.empty:
        fig.suptitle(title)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    plot_df = summary_df.sort_values(by=x_col)
    x_vals = plot_df[x_col].astype(str)

    metrics = [
        ("setup_time_mean", "Setup Time (s)"),
        ("sign_time_mean_mean", "Sign Time (s)"),
        ("verify_time_mean_mean", "Verify Time (s)"),
        ("avg_signature_size_mean", "Signature Size (bytes)"),
    ]

    for ax, (col, ylabel) in zip(axes, metrics):
        if col in plot_df.columns:
            ax.bar(x_vals, plot_df[col])
            ax.set_title(ylabel)
            ax.set_xlabel("OTS Type")
            ax.set_ylabel(ylabel)

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()



def plot_multi_line_subplots(
    summary_df: pd.DataFrame,
    x_col: str,
    group_col: str | None,
    metrics: list[tuple[str, str, str | None]],
    layout: tuple[int, int],
    title: str,
    output_path: str | Path,
):
    """
    Generic multi-subplot line plot.

    @ metrics format:
        [ (y_mean_col, ylabel, y_std_col_or_None), ... ]
    """
    output_path = ensure_plot_dir(output_path)
    rows, cols = layout
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    if summary_df.empty:
        fig.suptitle(title)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    for ax, (y_mean_col, ylabel, y_std_col) in zip(axes, metrics):
        if y_mean_col not in summary_df.columns:
            ax.set_title(f"{ylabel} (missing)")
            continue

        if group_col and group_col in summary_df.columns:
            for group_value, group_df in summary_df.groupby(group_col):
                group_df = group_df.sort_values(by=x_col)
                ax.plot(group_df[x_col], group_df[y_mean_col], marker="o", label=str(group_value))
                if y_std_col and y_std_col in group_df.columns:
                    lower = group_df[y_mean_col] - group_df[y_std_col].fillna(0)
                    upper = group_df[y_mean_col] + group_df[y_std_col].fillna(0)
                    ax.fill_between(group_df[x_col], lower, upper, alpha=0.15)
            ax.legend()
        else:
            plot_df = summary_df.sort_values(by=x_col)
            ax.plot(plot_df[x_col], plot_df[y_mean_col], marker="o")
            if y_std_col and y_std_col in plot_df.columns:
                lower = plot_df[y_mean_col] - plot_df[y_std_col].fillna(0)
                upper = plot_df[y_mean_col] + plot_df[y_std_col].fillna(0)
                ax.fill_between(plot_df[x_col], lower, upper, alpha=0.15)

        ax.set_title(ylabel)
        ax.set_xlabel(x_col)
        ax.set_ylabel(ylabel)

    # hide unused axes
    for i in range(len(metrics), len(axes)):
        axes[i].axis("off")

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_multi_bar_subplots(
    summary_df: pd.DataFrame,
    x_col: str,
    metrics: list[tuple[str, str]],
    layout: tuple[int, int],
    title: str,
    output_path: str | Path,
):
    """
    Generic multi subplot bar plot

    @ metrics format
        [ (y_mean_col, ylabel), ... ]
    """
    output_path = ensure_plot_dir(output_path)
    rows, cols = layout
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    if summary_df.empty:
        fig.suptitle(title)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    plot_df = summary_df.sort_values(by=x_col)

    for ax, (y_mean_col, ylabel) in zip(axes, metrics):
        if y_mean_col not in plot_df.columns:
            ax.set_title(f"{ylabel} (missing)")
            continue

        ax.bar(plot_df[x_col].astype(str), plot_df[y_mean_col])
        ax.set_title(ylabel)
        ax.set_xlabel(x_col)
        ax.set_ylabel(ylabel)

    # hide unused axes
    for i in range(len(metrics), len(axes)):
        axes[i].axis("off")

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()