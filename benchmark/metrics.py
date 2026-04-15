import csv
import hashlib
import json
import pickle
import statistics
from pathlib import Path
from typing import Iterable


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