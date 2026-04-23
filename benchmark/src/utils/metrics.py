from pathlib import Path
import csv
import json
import hashlib
import pickle
import statistics
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable

import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# basic helpers
# ---------------------------------------------------------
def digest32(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def serialized_size(obj: Any) -> int:
    return len(pickle.dumps(obj))


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.mean(values) if values else 0.0


def stdev(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.stdev(values) if len(values) >= 2 else 0.0


# ---------------------------------------------------------
# record normalization
# ---------------------------------------------------------
def normalize_record(record: Any) -> dict:
    if hasattr(record, "to_dict") and callable(record.to_dict):
        return record.to_dict()
    if is_dataclass(record):
        return asdict(record)
    if isinstance(record, dict):
        return record
    raise TypeError(f"Unsupported record type: {type(record)}")


def normalize_rows(rows: list[Any]) -> list[dict]:
    return [normalize_record(row) for row in rows]


# ---------------------------------------------------------
# file writing
# ---------------------------------------------------------
def write_csv(rows: list[Any], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    normalized_rows = normalize_rows(rows)

    if not normalized_rows:
        output_path.write_text("")
        return

    field_names = sorted({key for row in normalized_rows for key in row.keys()})
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(normalized_rows)


def write_json(obj: Any, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(obj, list):
        normalized_obj = []
        for item in obj:
            if isinstance(item, (str, int, float, bool)) or item is None:
                normalized_obj.append(item)
            else:
                normalized_obj.append(normalize_record(item))
        obj = normalized_obj
    elif not isinstance(obj, (dict, str, int, float, bool)) and obj is not None:
        obj = normalize_record(obj)

    output_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


# ---------------------------------------------------------
# dataframe + summary
# ---------------------------------------------------------
def rows_to_df(rows: list[Any]) -> pd.DataFrame:
    normalized_rows = normalize_rows(rows)
    if not normalized_rows:
        return pd.DataFrame()
    return pd.DataFrame(normalized_rows)


def save_summary(
    rows: list[Any],
    groupby_cols: list[str],
    metric_cols: list[str],
    output_path: str | Path,
) -> pd.DataFrame:
    summary_df = rows_to_df(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if summary_df.empty:
        summary_df.to_csv(output_path, index=False)
        return summary_df

    usable_metric_cols = [column for column in metric_cols if column in summary_df.columns]
    agg_map = {column: ["mean", "std"] for column in usable_metric_cols}

    summary_df = summary_df.groupby(groupby_cols, dropna=False).agg(agg_map).reset_index()

    flat_columns = []
    for column in summary_df.columns:
        if isinstance(column, tuple):
            left_name, right_name = column
            if right_name == "":
                flat_columns.append(left_name)
            else:
                flat_columns.append(f"{left_name}_{right_name}")
        else:
            flat_columns.append(column)
    summary_df.columns = flat_columns

    summary_df.to_csv(output_path, index=False)
    return summary_df


# ---------------------------------------------------------
# plotting helpers
# ---------------------------------------------------------
def _ensure_plot_path(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def plot_multiLine_subplots(
    summary_df: pd.DataFrame,
    x_col: str,
    group_col: str | None,
    metrics: list[tuple[str, str, str | None]],
    layout: tuple[int, int],
    title: str,
    output_path: str | Path,
) -> None:
    output_path = _ensure_plot_path(output_path)
    rows, cols = layout
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    if summary_df.empty:
        fig.suptitle(title)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    for axis, (y_mean_col, y_label, y_std_col) in zip(axes, metrics):
        if y_mean_col not in summary_df.columns:
            axis.set_title(f"{y_label} (missing)")
            continue

        if group_col and group_col in summary_df.columns:
            for group_value, group_df in summary_df.groupby(group_col):
                group_df = group_df.sort_values(by=x_col)
                axis.plot(group_df[x_col], group_df[y_mean_col], marker="o", label=str(group_value))
                if y_std_col and y_std_col in group_df.columns:
                    lower = group_df[y_mean_col] - group_df[y_std_col].fillna(0)
                    upper = group_df[y_mean_col] + group_df[y_std_col].fillna(0)
                    axis.fill_between(group_df[x_col], lower, upper, alpha=0.15)
            axis.legend()
        else:
            plot_df = summary_df.sort_values(by=x_col)
            axis.plot(plot_df[x_col], plot_df[y_mean_col], marker="o")
            if y_std_col and y_std_col in plot_df.columns:
                lower = plot_df[y_mean_col] - plot_df[y_std_col].fillna(0)
                upper = plot_df[y_mean_col] + plot_df[y_std_col].fillna(0)
                axis.fill_between(plot_df[x_col], lower, upper, alpha=0.15)

        axis.set_title(y_label)
        axis.set_xlabel(x_col)
        axis.set_ylabel(y_label)

    for index in range(len(metrics), len(axes)):
        axes[index].axis("off")

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_multiBar_subplots(
    summary_df: pd.DataFrame,
    x_col: str,
    metrics: list[tuple[str, str]],
    layout: tuple[int, int],
    title: str,
    output_path: str | Path,
) -> None:
    output_path = _ensure_plot_path(output_path)
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

    for axis, (y_mean_col, y_label) in zip(axes, metrics):
        if y_mean_col not in plot_df.columns:
            axis.set_title(f"{y_label} (missing)")
            continue

        axis.bar(plot_df[x_col].astype(str), plot_df[y_mean_col])
        axis.set_title(y_label)
        axis.set_xlabel(x_col)
        axis.set_ylabel(y_label)

    for index in range(len(metrics), len(axes)):
        axes[index].axis("off")

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()