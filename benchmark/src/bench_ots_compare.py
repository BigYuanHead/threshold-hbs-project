from dataclasses import asdict, dataclass

from benchmark.src.utils.metrics import serialized_size

# base libraries
from entities.party import Party
from entities.trusted_server import TrustedServer
from entities.untrusted_server import UntrustedServer
from entities.verifier import Verifier

# extension 5 libraries
from extension_5.winternitz_standardized import WinternitzStandardized
from extension_5.wz_setup import setup_winternitz_key_material
from extension_5.wz_party import WinternitzParty
from extension_5.wz_server import WinternitzUntrustedServer
from extension_5.wz_verifier import WinternitzVerifier

# timing
from benchmark.src.datatypes.utils_dt import TimeStats
from benchmark.src.utils.timer import now, timed, summarize_time_measure





def build_lamport_threshold_system(total_keys: int,
                                   n_parties: int):
    """
        Build one Lamport threshold system instance.

        @ input:
            - total_keys: number of one-time keys
            - n_parties: number of threshold parties

        @ return:
            - public_params
            - parties
            - signer
            - verifier
    """
    trusted_server = TrustedServer(total_keys=total_keys,
                                   n_parties=n_parties)
    public_params, share_bundles = trusted_server.setup()

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



def build_winternitz_threshold_system(total_keys: int,
                                      n_parties: int,
                                      w: int):
    """
        Build one Winternitz threshold system instance.

        @ input:
            - total_keys: number of one-time keys
            - n_parties: number of threshold parties
            - w: Winternitz parameter

        @ return:
            - public_params
            - parties
            - signer
            - verifier
    """
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




def run_lamport_threshold_once(total_keys: int,
                               n_parties: int) -> OtsRunResult:
    """
        Run one Lamport-threshold benchmark.
    """
    t0 = now()
    _, parties, signer, verifier = build_lamport_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )
    setup_time = now() - t0

    sign_times: list[float] = []
    verify_times: list[float] = []
    signature_sizes: list[int] = []
    success_count = 0

    for key_id in range(total_keys):
        message = f"lamport-threshold-message-{key_id}".encode()

        t1 = now()
        signed_data = signer.sign(
            message=message,
            keyid=key_id,
            parties=parties,
        )
        sign_times.append(now() - t1)

        signature_sizes.append(serialized_size(signed_data))

        t2 = now()
        ok = verifier.verify(message, signed_data)
        verify_times.append(now() - t2)

        if ok:
            success_count += 1

    sign_stats = summarize_measurements(sign_times)
    verify_stats = summarize_measurements(verify_times)

    return OtsRunResult(
        benchmark_name="ots_compare",
        ots_type="lamport",
        total_keys=total_keys,
        n_parties=n_parties,
        setup_time=setup_time,

        success_rate=success_count / total_keys,
        avg_signature_size=sum(signature_sizes) / len(signature_sizes),

        sign_time_mean=sign_stats.mean,
        sign_time_stdev=sign_stats.stdev,
        sign_time_min=sign_stats.min_value,
        sign_time_max=sign_stats.max_value,

        verify_time_mean=verify_stats.mean,
        verify_time_stdev=verify_stats.stdev,
        verify_time_min=verify_stats.min_value,
        verify_time_max=verify_stats.max_value,
    )



def run_winternitz_threshold_once(total_keys: int,
                                  n_parties: int,
                                  w: int) -> OtsRunResult:
    """
        Run one Winternitz-threshold benchmark.
    """
    t0 = now()
    _, parties, signer, verifier = build_winternitz_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
        w=w,
    )
    setup_time = now() - t0

    sign_times: list[float] = []
    verify_times: list[float] = []
    signature_sizes: list[int] = []
    success_count = 0

    for key_id in range(total_keys):
        message = f"winternitz-threshold-message-{key_id}".encode()

        t1 = now()
        signed_data = signer.sign(
            message=message,
            keyid=key_id,
            parties=parties,
        )
        sign_times.append(now() - t1)

        signature_sizes.append(serialized_size(signed_data))

        t2 = now()
        ok = verifier.verify(message, signed_data)
        verify_times.append(now() - t2)

        if ok:
            success_count += 1

    sign_stats = summarize_measurements(sign_times)
    verify_stats = summarize_measurements(verify_times)

    return OtsRunResult(
        benchmark_name="ots_compare",
        ots_type="winternitz",
        total_keys=total_keys,
        n_parties=n_parties,
        setup_time=setup_time,

        success_rate=success_count / total_keys,
        avg_signature_size=sum(signature_sizes) / len(signature_sizes),

        sign_time_mean=sign_stats.mean,
        sign_time_stdev=sign_stats.stdev,
        sign_time_min=sign_stats.min_value,
        sign_time_max=sign_stats.max_value,

        verify_time_mean=verify_stats.mean,
        verify_time_stdev=verify_stats.stdev,
        verify_time_min=verify_stats.min_value,
        verify_time_max=verify_stats.max_value,

        w=w,
    )



def benchmark_lamport_vs_winternitz(total_keys: int,
                                    n_parties: int,
                                    w: int,
                                    repeats: int = 5) -> tuple[list[OtsRunResult], list[OtsBenchSummary]]:
    """
        Compare Lamport threshold and Winternitz threshold under one fixed w.
    """
    config = OtsCompareConfig(
        total_keys=total_keys,
        n_parties=n_parties,
        repeats=repeats,
        w=w,
    )
    rows: list[OtsRunResult] = []

    for repeat in range(config.repeats):
        lamport_row = run_lamport_threshold_once(
            total_keys=config.total_keys,
            n_parties=config.n_parties,
        )
        lamport_row.repeat = repeat
        rows.append(lamport_row)

        winternitz_row = run_winternitz_threshold_once(
            total_keys=config.total_keys,
            n_parties=config.n_parties,
            w=config.w,
        )
        winternitz_row.repeat = repeat
        rows.append(winternitz_row)

    lamport_rows = [row for row in rows if row.ots_type == "lamport"]
    winternitz_rows = [row for row in rows if row.ots_type == "winternitz"]

    summaries = [
        OtsBenchSummary(
            benchmark_name="ots_compare",
            ots_type="lamport",
            total_keys=config.total_keys,
            n_parties=config.n_parties,
            repeats=config.repeats,
            setup_time_mean=sum(row.setup_time for row in lamport_rows) / config.repeats,
            success_rate_mean=sum(row.success_rate for row in lamport_rows) / config.repeats,
            avg_signature_size_mean=sum(row.avg_signature_size for row in lamport_rows) / config.repeats,
            sign_time_mean_mean=sum(row.sign_time_mean for row in lamport_rows) / config.repeats,
            verify_time_mean_mean=sum(row.verify_time_mean for row in lamport_rows) / config.repeats,
        ),
        OtsBenchSummary(
            benchmark_name="ots_compare",
            ots_type="winternitz",
            total_keys=config.total_keys,
            n_parties=config.n_parties,
            repeats=config.repeats,
            w=config.w,
            setup_time_mean=sum(row.setup_time for row in winternitz_rows) / config.repeats,
            success_rate_mean=sum(row.success_rate for row in winternitz_rows) / config.repeats,
            avg_signature_size_mean=sum(row.avg_signature_size for row in winternitz_rows) / config.repeats,
            sign_time_mean_mean=sum(row.sign_time_mean for row in winternitz_rows) / config.repeats,
            verify_time_mean_mean=sum(row.verify_time_mean for row in winternitz_rows) / config.repeats,
        ),
    ]

    return rows, summaries



def benchmark_winternitz_by_w(total_keys: int,
                              n_parties: int,
                              w_values: list[int],
                              repeats: int = 5) -> tuple[list[OtsRunResult], list[OtsBenchSummary]]:
    """
        Run Winternitz threshold benchmark while only changing w.
    """
    config = WinternitzSweepConfig(
        total_keys=total_keys,
        n_parties=n_parties,
        w_values=w_values,
        repeats=repeats,
    )
    rows: list[OtsRunResult] = []
    summaries: list[OtsBenchSummary] = []

    for w in config.w_values:
        current_rows: list[OtsRunResult] = []

        for repeat in range(config.repeats):
            row = run_winternitz_threshold_once(
                total_keys=config.total_keys,
                n_parties=config.n_parties,
                w=w,
            )
            row.repeat = repeat
            rows.append(row)
            current_rows.append(row)

        summaries.append(
            OtsBenchSummary(
                benchmark_name="winternitz_by_w",
                ots_type="winternitz",
                total_keys=config.total_keys,
                n_parties=config.n_parties,
                repeats=config.repeats,
                w=w,
                setup_time_mean=sum(row.setup_time for row in current_rows) / config.repeats,
                success_rate_mean=sum(row.success_rate for row in current_rows) / config.repeats,
                avg_signature_size_mean=sum(row.avg_signature_size for row in current_rows) / config.repeats,
                sign_time_mean_mean=sum(row.sign_time_mean for row in current_rows) / config.repeats,
                verify_time_mean_mean=sum(row.verify_time_mean for row in current_rows) / config.repeats,
            )
        )

    return rows, summaries