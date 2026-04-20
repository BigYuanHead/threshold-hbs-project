import time

from benchmark.src.utils.metrics import serialized_size, summarise_times

from entities.party import Party
from entities.trusted_server import TrustedServer
from entities.untrusted_server import UntrustedServer
from entities.verifier import Verifier

from extension_5.winternitz_standardized import WinternitzStandardized
from extension_5.wz_setup import setup_winternitz_key_material
from extension_5.wz_party import WinternitzParty
from extension_5.wz_server import WinternitzUntrustedServer
from extension_5.wz_verifier import WinternitzVerifier


def build_lamport_threshold_system(total_keys: int, n_parties: int):
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


def build_winternitz_threshold_system(total_keys: int, n_parties: int, w: int):
    backend = WinternitzStandardized(w=w)

    public_params, party_share_bundles = setup_winternitz_key_material(
        total_keys=total_keys,
        n_parties=n_parties,
        backend=backend,
    )

    parties = [
        WinternitzParty(
            party_id=bundle["party_id"],
            share_bundle=bundle,
            backend=backend,
        )
        for bundle in party_share_bundles
    ]

    signer = WinternitzUntrustedServer(
        public_params=public_params,
        backend=backend,
    )

    verifier = WinternitzVerifier(
        root=public_params["root"],
        total_keys=public_params["total_keys"],
        backend=backend,
    )

    return public_params, parties, signer, verifier


def run_lamport_threshold_once(total_keys: int, n_parties: int) -> dict:
    t0 = time.perf_counter()
    public_params, parties, signer, verifier = build_lamport_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )
    setup_time = time.perf_counter() - t0

    sign_times = []
    verify_times = []
    signature_sizes = []
    success_count = 0

    for keyid in range(total_keys):
        message = f"lamport-threshold-message-{keyid}".encode()

        t1 = time.perf_counter()
        signed_data = signer.sign(
            message=message,
            keyid=keyid,
            parties=parties,
        )
        sign_times.append(time.perf_counter() - t1)

        signature_sizes.append(serialized_size(signed_data))

        t2 = time.perf_counter()
        ok = verifier.verify(message, signed_data)
        verify_times.append(time.perf_counter() - t2)

        success_count += int(ok)

    return {
        "scheme": "threshold",
        "ots_type": "lamport",
        "total_keys": total_keys,
        "n_parties": n_parties,
        "setup_time": setup_time,
        "success_rate": success_count / total_keys,
        "avg_signature_size": sum(signature_sizes) / len(signature_sizes),
        **summarise_times(sign_times, "sign_time"),
        **summarise_times(verify_times, "verify_time"),
    }


def run_winternitz_threshold_once(total_keys: int, n_parties: int, w: int) -> dict:
    t0 = time.perf_counter()
    public_params, parties, signer, verifier = build_winternitz_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
        w=w,
    )
    setup_time = time.perf_counter() - t0

    sign_times = []
    verify_times = []
    signature_sizes = []
    success_count = 0

    for keyid in range(total_keys):
        message = f"winternitz-threshold-message-{keyid}".encode()

        t1 = time.perf_counter()
        signed_data = signer.sign(
            message=message,
            keyid=keyid,
            parties=parties,
        )
        sign_times.append(time.perf_counter() - t1)

        signature_sizes.append(serialized_size(signed_data))

        t2 = time.perf_counter()
        ok = verifier.verify(message, signed_data)
        verify_times.append(time.perf_counter() - t2)

        success_count += int(ok)

    return {
        "scheme": "threshold",
        "ots_type": "winternitz",
        "w": w,
        "total_keys": total_keys,
        "n_parties": n_parties,
        "setup_time": setup_time,
        "success_rate": success_count / total_keys,
        "avg_signature_size": sum(signature_sizes) / len(signature_sizes),
        **summarise_times(sign_times, "sign_time"),
        **summarise_times(verify_times, "verify_time"),
    }


def benchmark_lamport_vs_winternitz(total_keys: int, n_parties: int, w: int, repeats: int = 5):
    rows = []

    for repeat in range(repeats):
        lamport_row = run_lamport_threshold_once(total_keys=total_keys, n_parties=n_parties)
        lamport_row["repeat"] = repeat
        rows.append(lamport_row)

        wz_row = run_winternitz_threshold_once(total_keys=total_keys, n_parties=n_parties, w=w)
        wz_row["repeat"] = repeat
        rows.append(wz_row)

    return rows


def benchmark_winternitz_by_w(total_keys: int, n_parties: int, w_values: list[int], repeats: int = 5):
    rows = []

    for w in w_values:
        for repeat in range(repeats):
            row = run_winternitz_threshold_once(
                total_keys=total_keys,
                n_parties=n_parties,
                w=w,
            )
            row["repeat"] = repeat
            rows.append(row)

    return rows