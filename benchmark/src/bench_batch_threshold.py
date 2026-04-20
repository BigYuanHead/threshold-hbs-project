import time

from benchmark.src.utils.metrics import serialized_size, summarise_times
from extension_3.batch_threshold import BatchThresholdHBS

from entities.party import Party
from entities.trusted_server import TrustedServer
from entities.untrusted_server import UntrustedServer
from entities.verifier import Verifier


def build_threshold_system(total_keys: int, n_parties: int):
    trusted = TrustedServer(total_keys=total_keys, n_parties=n_parties)
    public_params, share_bundles = trusted.setup()

    parties = [
        Party(
            party_id=bundle["party_id"],
            share_bundle=bundle,
        )
        for bundle in share_bundles
    ]

    signer = UntrustedServer(public_params=public_params)
    verifier = Verifier(
        root=public_params["root"],
        total_keys=public_params["total_keys"],
    )
    return public_params, parties, signer, verifier


def make_messages(batch_size: int, prefix: str = "batch-msg") -> list[bytes]:
    return [f"{prefix}-{i}".encode() for i in range(batch_size)]


def run_batch_once(total_keys: int, n_parties: int, batch_size: int, keyid: int = 0) -> dict:
    if total_keys <= 0:
        raise ValueError("total_keys must be positive")
    if n_parties <= 0:
        raise ValueError("n_parties must be positive")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    _, parties, signer, verifier = build_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )

    batch_hbs = BatchThresholdHBS(signer=signer, verifier=verifier)
    messages = make_messages(batch_size)

    t1 = time.perf_counter()
    batch_pack = batch_hbs.batch_sign(
        messages=messages,
        keyid=keyid,
        parties=parties,
    )
    batch_sign_time = time.perf_counter() - t1

    verify_times = []
    success_count = 0

    for idx, msg in enumerate(messages):
        t2 = time.perf_counter()
        ok = batch_hbs.batch_verify(msg, idx, batch_pack)
        verify_times.append(time.perf_counter() - t2)
        success_count += int(ok)

    total_batch_verify_time = sum(verify_times)

    return {
        "scheme": "batch_threshold",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "batch_size": batch_size,
        "batch_sign_time": batch_sign_time,
        "total_batch_verify_time": total_batch_verify_time,
        "per_message_sign_time": batch_sign_time / batch_size,
        "per_message_verify_time": total_batch_verify_time / batch_size,
        "batch_pack_size": serialized_size(batch_pack),
        "success_rate": success_count / batch_size,
        **summarise_times(verify_times, "verify_time"),
    }


def benchmark_batch_by_size(total_keys: int, n_parties: int, batch_sizes: list[int], repeats: int = 5):
    rows = []
    for batch_size in batch_sizes:
        for repeat in range(repeats):
            row = run_batch_once(
                total_keys=total_keys,
                n_parties=n_parties,
                batch_size=batch_size,
                keyid=0,
            )
            row["repeat"] = repeat
            rows.append(row)
    return rows


def run_nonbatch_once(total_keys: int, n_parties: int, message_count: int) -> dict:
    if total_keys < message_count:
        raise ValueError("total_keys must be >= message_count for non-batch test")

    _, parties, signer, verifier = build_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )

    messages = make_messages(message_count, prefix="nonbatch-msg")

    sign_times = []
    verify_times = []
    total_size = 0
    success_count = 0

    for keyid, msg in enumerate(messages):
        t1 = time.perf_counter()
        signed_data = signer.sign(
            message=msg,
            keyid=keyid,
            parties=parties,
        )
        sign_times.append(time.perf_counter() - t1)
        total_size += serialized_size(signed_data)

        t2 = time.perf_counter()
        ok = verifier.verify(msg, signed_data)
        verify_times.append(time.perf_counter() - t2)
        success_count += int(ok)

    total_sign_time = sum(sign_times)
    total_verify_time = sum(verify_times)

    return {
        "scheme": "nonbatch_threshold",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "message_count": message_count,
        "total_sign_time": total_sign_time,
        "total_verify_time": total_verify_time,
        "per_message_sign_time": total_sign_time / message_count,
        "per_message_verify_time": total_verify_time / message_count,
        "total_output_size": total_size,
        "success_rate": success_count / message_count,
        **summarise_times(sign_times, "sign_time"),
        **summarise_times(verify_times, "verify_time"),
    }


def compare_batch_vs_nonbatch(total_keys: int, n_parties: int, message_count: int, repeats: int = 5):
    rows = []

    for repeat in range(repeats):
        nonbatch_row = run_nonbatch_once(
            total_keys=total_keys,
            n_parties=n_parties,
            message_count=message_count,
        )
        nonbatch_row["repeat"] = repeat
        rows.append(nonbatch_row)

        batch_row = run_batch_once(
            total_keys=total_keys,
            n_parties=n_parties,
            batch_size=message_count,
            keyid=0,
        )
        batch_row["repeat"] = repeat
        rows.append(batch_row)

    return rows


def benchmark_batch_failures(total_keys: int, n_parties: int, batch_size: int) -> dict:
    _, parties, signer, verifier = build_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )

    batch_hbs = BatchThresholdHBS(signer=signer, verifier=verifier)
    messages = make_messages(batch_size)
    batch_pack = batch_hbs.batch_sign(messages=messages, keyid=0, parties=parties)

    verify_correct = batch_hbs.batch_verify(messages[0], 0, batch_pack)
    verify_wrong_message = batch_hbs.batch_verify(b"wrong-message", 0, batch_pack)
    verify_wrong_index = batch_hbs.batch_verify(messages[0], batch_size + 10, batch_pack)

    bad_batch_pack = dict(batch_pack)
    bad_paths = list(batch_pack["message_paths"])
    if bad_paths and bad_paths[0]:
        tampered_path = list(bad_paths[0])
        tampered_path[0] = b"wrong"
        bad_paths[0] = tampered_path
    bad_batch_pack["message_paths"] = bad_paths

    verify_wrong_path = batch_hbs.batch_verify(messages[0], 0, bad_batch_pack)

    return {
        "scheme": "batch_failure",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "batch_size": batch_size,
        "verify_correct": bool(verify_correct),
        "verify_wrong_message_rejected": not bool(verify_wrong_message),
        "verify_wrong_index_rejected": not bool(verify_wrong_index),
        "verify_wrong_path_rejected": not bool(verify_wrong_path),
    }