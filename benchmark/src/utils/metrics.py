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


# >>>>>>>>>>>>>>>>>>>> basic helpers >>>>>>>>>>>>>>>>>>>>
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


# >>>>>>>>>>>>>>>>>>>> record normalize >>>>>>>>>>>>>>>>>>>>
def normalize_record(record: Any) -> dict:
    # get to_dict method in my dataclass
    if hasattr(record, "to_dict") and callable(record.to_dict):
        return record.to_dict()
    if is_dataclass(record): # dataclass
        return asdict(record)
    if isinstance(record, dict):
        return record
    raise TypeError(f"Unsupported record type: {type(record)}")


def normalize_rows(rows: list) -> list[dict]:
    return [normalize_record(row) for row in rows]


# >>>>>>>>>>>>>>>>>>>> file writing >>>>>>>>>>>>>>>>>>>>
def write_csv(rows: list, output_path: Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    normalized_rows = normalize_rows(rows)

    if not normalized_rows:
        output_path.write_text("")
        return

    fieldName_list = sorted({key for row in normalized_rows for key in row.keys()})
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldName_list)
        writer.writeheader()
        writer.writerows(normalized_rows)


def write_json(obj: Any, output_path: Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(obj, list):
        normalizedObj_list = []
        for item in obj:
            if isinstance(item, (str, int, float, bool)) or item is None:
                normalizedObj_list.append(item)
            else:
                normalizedObj_list.append(normalize_record(item))
        obj = normalizedObj_list
    elif not isinstance(obj, (dict, str, int, float, bool)) and obj is not None:
        obj = normalize_record(obj)

    output_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


# >>>>>>>>>>>>>>>>>>>> dataFrame and summary Opts >>>>>>>>>>>>>>>>>>>>
def rows_to_df(rows: list) -> pd.DataFrame:
    normalized_rows = normalize_rows(rows)
    if not normalized_rows:
        return pd.DataFrame()
    return pd.DataFrame(normalized_rows)


def save_summary(
    rows: list,
    groupby_cols: list[str],
    metric_cols: list[str],
    output_path: Path,
) -> pd.DataFrame:
    summary_df = rows_to_df(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if summary_df.empty:
        summary_df.to_csv(output_path, index=False)
        return summary_df

    usableMetric_list = [column for column in metric_cols if column in summary_df.columns]
    aggMap_dict = {column: ["mean", "std"] for column in usableMetric_list}

    summary_df = summary_df.groupby(groupby_cols, dropna=False).agg(aggMap_dict).reset_index()

    flatColumn_list = []
    for column in summary_df.columns:
        if isinstance(column, tuple):
            leftName, rightName = column
            if rightName == "":
                flatColumn_list.append(leftName)
            else:
                flatColumn_list.append(f"{leftName}_{rightName}")
        else:
            flatColumn_list.append(column)
    summary_df.columns = flatColumn_list

    summary_df.to_csv(output_path, index=False)
    return summary_df


# >>>>>>>>>>>>>>>>>>>> plot helpers >>>>>>>>>>>>>>>>>>>>
def _ensure_plot_path(path: Path) -> Path:
    path = Path(path)
    # create folder
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def plot_multiLine_subplots(
    summary_df: pd.DataFrame,
    x_col: str,
    group_col: str | None,
    metrics: list[tuple[str, str, str | None]],
    layout: tuple[int, int],
    title: str,
    output_path: Path,
):
    output_path = _ensure_plot_path(output_path)
    # Make one figure with several line subplots.
    rows, cols = layout
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    if summary_df.empty:
        fig.suptitle(title)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return

    for axis, (yMean_col, yLabel, yStd_col) in zip(axes, metrics):
        if yMean_col not in summary_df.columns:
            axis.set_title(f"{yLabel} (missing)")
            continue

        if group_col and group_col in summary_df.columns:
            for groupValue, group_df in summary_df.groupby(group_col):
                group_df = group_df.sort_values(by=x_col)
                axis.plot(group_df[x_col], group_df[yMean_col], marker="o", label=str(groupValue))
                if yStd_col and yStd_col in group_df.columns:
                    lower = group_df[yMean_col] - group_df[yStd_col].fillna(0)
                    upper = group_df[yMean_col] + group_df[yStd_col].fillna(0)
                    axis.fill_between(group_df[x_col], lower, upper, alpha=0.15)
            axis.legend()
        else:
            plotDf = summary_df.sort_values(by=x_col)
            axis.plot(plotDf[x_col], plotDf[yMean_col], marker="o")
            if yStd_col and yStd_col in plotDf.columns:
                lower = plotDf[yMean_col] - plotDf[yStd_col].fillna(0)
                upper = plotDf[yMean_col] + plotDf[yStd_col].fillna(0)
                axis.fill_between(plotDf[x_col], lower, upper, alpha=0.15)

        axis.set_title(yLabel)
        axis.set_xlabel(x_col)
        axis.set_ylabel(yLabel)

    for empty_index in range(len(metrics), len(axes)):
        axes[empty_index].axis("off")

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
    output_path: Path,
):
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

    plotDf = summary_df.sort_values(by=x_col)

    for axis, (yMean_col, yLabel) in zip(axes, metrics):
        if yMean_col not in plotDf.columns:
            axis.set_title(f"{yLabel} (missing)")
            continue

        axis.bar(plotDf[x_col].astype(str), plotDf[yMean_col])
        axis.set_title(yLabel)
        axis.set_xlabel(x_col)
        axis.set_ylabel(yLabel)

    for empty_index in range(len(metrics), len(axes)):
        axes[empty_index].axis("off")

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def build_relative_overhead_df(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
        relative_overhead = threshold / baseline
    """
    if summary_df.empty:
        return pd.DataFrame()

    # split baseline and threshold rows first
    baselineDf = summary_df[summary_df["benchmark_name"] == "baseline"].copy()
    thresholdDf = summary_df[summary_df["benchmark_name"] == "threshold"].copy()

    if baselineDf.empty or thresholdDf.empty:
        return pd.DataFrame()

    mergedDf = baselineDf.merge(
        thresholdDf,
        on="total_keys",
        suffixes=("_baseline", "_threshold"),
    )

    relativeDf = pd.DataFrame()
    relativeDf["total_keys"] = mergedDf["total_keys"]

    # compute threshold / baseline
    relativeDf["setup_time_ratio"] = (
        mergedDf["setup_time_mean_threshold"] /
        mergedDf["setup_time_mean_baseline"]
    )
    relativeDf["sign_time_ratio"] = (
        mergedDf["sign_time_mean_mean_threshold"] /
        mergedDf["sign_time_mean_mean_baseline"]
    )
    relativeDf["verify_time_ratio"] = (
        mergedDf["verify_time_mean_mean_threshold"] /
        mergedDf["verify_time_mean_mean_baseline"]
    )
    relativeDf["signature_size_ratio"] = (
        mergedDf["avg_signature_size_mean_threshold"] /
        mergedDf["avg_signature_size_mean_baseline"]
    )

    return relativeDf