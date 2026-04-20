import time

from benchmark.src.utils.metrics import serialized_size, summarise_times

from extension_1.kofn_setup import setup_kofn_key_material
from extension_1.kofn_party import KOfNParty
from extension_1.kofn_server import KOfNUntrustedServer
from extension_1.kofn_verifier import KOfNVerifier


def build_kofn_system(total_keys: int, n_parties: int, threshold_k: int):
    public_params, party_share_bundles = setup_kofn_key_material(
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
    )

    parties = [
        KOfNParty(
            party_id=bundle["party_id"],
            share_bundle=bundle,
        )
        for bundle in party_share_bundles
    ]

    signer = KOfNUntrustedServer(public_params)
    verifier = KOfNVerifier(
        root=public_params["root"],
        total_keys=public_params["total_keys"],
    )

    return public_params, parties, signer, verifier


def run_kofn_once(total_keys: int, n_parties: int, threshold_k: int) -> dict:
    if total_keys <= 0:
        raise ValueError("total_keys must be positive")
    if n_parties <= 0:
        raise ValueError("n_parties must be positive")
    if threshold_k <= 0 or threshold_k > n_parties:
        raise ValueError("threshold_k must satisfy 1 <= k <= n_parties")

    t0 = time.perf_counter()
    public_params, parties, signer, verifier = build_kofn_system(
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
    )
    setup_time = time.perf_counter() - t0

    sign_times = []
    verify_times = []
    signature_sizes = []
    success_count = 0

    # 每次都选前 k 个 party，保证可重复
    selected_parties = parties[:threshold_k]

    for keyid in range(total_keys):
        message = f"kofn-message-{keyid}".encode()

        t1 = time.perf_counter()
        signed_data = signer.sign(
            message=message,
            keyid=keyid,
            parties=selected_parties,
        )
        sign_times.append(time.perf_counter() - t1)

        signature_sizes.append(serialized_size(signed_data))

        t2 = time.perf_counter()
        ok = verifier.verify(message, signed_data)
        verify_times.append(time.perf_counter() - t2)

        success_count += int(ok)

    return {
        "scheme": "kofn",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "threshold_k": threshold_k,
        "setup_time": setup_time,
        "success_rate": success_count / total_keys,
        "avg_signature_size": sum(signature_sizes) / len(signature_sizes),
        **summarise_times(sign_times, "sign_time"),
        **summarise_times(verify_times, "verify_time"),
    }


def benchmark_kofn(total_keys: int, n_parties: int, threshold_k: int, repeats: int = 5):
    rows = []
    for repeat in range(repeats):
        row = run_kofn_once(
            total_keys=total_keys,
            n_parties=n_parties,
            threshold_k=threshold_k,
        )
        row["repeat"] = repeat
        rows.append(row)
    return rows


def benchmark_kofn_by_k(total_keys: int, n_parties: int, k_values: list[int], repeats: int = 5):
    rows = []
    for k in k_values:
        for repeat in range(repeats):
            row = run_kofn_once(
                total_keys=total_keys,
                n_parties=n_parties,
                threshold_k=k,
            )
            row["repeat"] = repeat
            rows.append(row)
    return rows


def benchmark_kofn_failures(total_keys: int, n_parties: int, threshold_k: int) -> dict:
    public_params, parties, signer, verifier = build_kofn_system(
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
    )

    selected_parties = parties[:threshold_k]
    message = b"hello k-of-n threshold"
    keyid = 0

    signed_data = signer.sign(
        message=message,
        keyid=keyid,
        parties=selected_parties,
    )

    verify_correct = verifier.verify(message, signed_data)
    verify_wrong_message = verifier.verify(b"wrong message", signed_data)

    # less than k
    try:
        signer.sign(
            message=b"not enough parties",
            keyid=1,
            parties=parties[: threshold_k - 1],
        )
        less_than_k_rejected = False
    except ValueError:
        less_than_k_rejected = True

    # reuse same keyid / subtree keyid
    try:
        signer.sign(
            message=b"reuse same subtree keyid",
            keyid=keyid,
            parties=selected_parties,
        )
        reuse_keyid_rejected = False
    except ValueError:
        reuse_keyid_rejected = True

    return {
        "scheme": "kofn_failure",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "threshold_k": threshold_k,
        "verify_correct": bool(verify_correct),
        "verify_wrong_message_rejected": not bool(verify_wrong_message),
        "less_than_k_rejected": less_than_k_rejected,
        "reuse_keyid_rejected": reuse_keyid_rejected,
    }