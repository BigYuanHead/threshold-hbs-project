import time

from entities.party import Party
from entities.trusted_server import TrustedServer
from entities.untrusted_server import UntrustedServer
from entities.verifier import Verifier
from benchmark.metrics import digest32, serialized_size, summarise_times


def build_threshold_system(total_keys: int, n_parties: int):
    trusted = TrustedServer(total_keys=total_keys, n_parties=n_parties)
    public_params, share_bundles = trusted.setup()

    parties = [
        Party(party_id=bundle["party_id"], share_bundle=bundle)
        for bundle in share_bundles
    ]
    untrusted = UntrustedServer(public_params=public_params)
    verifier = Verifier(root=public_params["root"], total_keys=public_params["total_keys"])

    return trusted, public_params, parties, untrusted, verifier


def run_threshold_once(total_keys: int, n_parties: int) -> dict:
    if total_keys <= 0:
        raise ValueError("total_keys must be positive")
    if n_parties <= 0:
        raise ValueError("n_parties must be positive")

    t0 = time.perf_counter()
    _, public_params, parties, untrusted, verifier = build_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )
    setup_time = time.perf_counter() - t0

    sign_times = []
    verify_times = []
    signature_sizes = []
    path_lengths = []
    success_count = 0

    for keyid in range(total_keys):
        msg = digest32(f"threshold-message-{keyid}".encode())

        t1 = time.perf_counter()
        signed_data = untrusted.sign(message=msg, keyid=keyid, parties=parties)
        sign_times.append(time.perf_counter() - t1)

        signature_sizes.append(serialized_size(signed_data))
        path_lengths.append(len(signed_data["path"]))

        t2 = time.perf_counter()
        ok = verifier.verify(msg, signed_data)
        verify_times.append(time.perf_counter() - t2)

        success_count += int(ok)

    return {
        "scheme": "threshold",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "setup_time": setup_time,
        "success_rate": success_count / total_keys,
        "avg_signature_size": sum(signature_sizes) / len(signature_sizes),
        "avg_path_length": sum(path_lengths) / len(path_lengths),
        **summarise_times(sign_times, "sign_time"),
        **summarise_times(verify_times, "verify_time"),
        "root_size": len(public_params["root"]),
    }


def benchmark_threshold(total_keys: int, n_parties: int, repeats: int = 5) -> tuple[list[dict], dict]:
    rows = []
    for repeat in range(repeats):
        row = run_threshold_once(total_keys=total_keys, n_parties=n_parties)
        row["repeat"] = repeat
        rows.append(row)

    summary = {
        "scheme": "threshold",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "repeats": repeats,
        "setup_time_mean": sum(r["setup_time"] for r in rows) / repeats,
        "success_rate_mean": sum(r["success_rate"] for r in rows) / repeats,
        "avg_signature_size_mean": sum(r["avg_signature_size"] for r in rows) / repeats,
        "avg_path_length_mean": sum(r["avg_path_length"] for r in rows) / repeats,
        "sign_time_mean_mean": sum(r["sign_time_mean"] for r in rows) / repeats,
        "verify_time_mean_mean": sum(r["verify_time_mean"] for r in rows) / repeats,
    }
    return rows, summary