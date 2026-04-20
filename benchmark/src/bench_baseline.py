import time

from core.baseline import StatefulHBS
from benchmark.src.utils.metrics import digest32, serialized_size, summarise_times


def run_baseline_once(total_keys: int) -> dict:
    if total_keys <= 0:
        raise ValueError("total_keys must be positive")

    t0 = time.perf_counter()
    hbs = StatefulHBS(total_keys=total_keys)
    setup_time = time.perf_counter() - t0

    sign_times = []
    verify_times = []
    signature_sizes = []
    path_lengths = []
    success_count = 0

    for keyid in range(total_keys):
        msg = digest32(f"baseline-message-{keyid}".encode())

        t1 = time.perf_counter()
        signed_data = hbs.sign(keyid, msg)
        sign_times.append(time.perf_counter() - t1)

        signature_sizes.append(serialized_size(signed_data))
        path_lengths.append(len(signed_data["path"]))

        t2 = time.perf_counter()
        ok = hbs.verify(msg, signed_data)
        verify_times.append(time.perf_counter() - t2)

        success_count += int(ok)

    return {
        "scheme": "baseline",
        "total_keys": total_keys,
        "setup_time": setup_time,
        "success_rate": success_count / total_keys,
        "avg_signature_size": sum(signature_sizes) / len(signature_sizes),
        "avg_path_length": sum(path_lengths) / len(path_lengths),
        **summarise_times(sign_times, "sign_time"),
        **summarise_times(verify_times, "verify_time"),
    }


def benchmark_baseline(total_keys: int, repeats: int = 5) -> tuple[list[dict], dict]:
    rows = []
    for repeat in range(repeats):
        row = run_baseline_once(total_keys=total_keys)
        row["repeat"] = repeat
        rows.append(row)

    summary = {
        "scheme": "baseline",
        "total_keys": total_keys,
        "repeats": repeats,
        "setup_time_mean": sum(r["setup_time"] for r in rows) / repeats,
        "success_rate_mean": sum(r["success_rate"] for r in rows) / repeats,
        "avg_signature_size_mean": sum(r["avg_signature_size"] for r in rows) / repeats,
        "avg_path_length_mean": sum(r["avg_path_length"] for r in rows) / repeats,
        "sign_time_mean_mean": sum(r["sign_time_mean"] for r in rows) / repeats,
        "verify_time_mean_mean": sum(r["verify_time_mean"] for r in rows) / repeats,
    }
    return rows, summary