from dataclasses import asdict, dataclass

from benchmark.src.utils.metrics import serialized_size
from benchmark.src.utils.timer import now

# timing
from benchmark.src.datatypes.utils_dt import TimeStats
from benchmark.src.utils.timer import now, timed, summarize_time_measure


# extension 1 libraries
from extension_1.kofn_setup import setup_kofn_key_material
from extension_1.kofn_party import KOfNParty
from extension_1.kofn_server import KOfNUntrustedServer
from extension_1.kofn_verifier import KOfNVerifier

# datatypes
from benchmark.src.datatypes.all_summary_dt import KOfNBenchSummary
from benchmark.src.datatypes.all_cfgs_dt import KOfNBenchConfig, KOfNCompareConfig
from benchmark.src.datatypes.all_result_dt import KOfNRunResult, KOfNFailureResult




def build_kofn_system(total_keys: int,
                      n_parties: int,
                      threshold_k: int):
    """
        Build one k-of-n threshold system instance.

        @ input:
            - total_keys: number of one-time keys
            - n_parties: number of total parties
            - threshold_k: threshold value k

        @ return:
            - public_params
            - parties
            - signer
            - verifier
    """
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



def run_kofn_once(total_keys: int,
                  n_parties: int,
                  threshold_k: int) -> KOfNRunResult:
    """
        Run the k-of-n threshold HBS once.

        @ input:
            - total_keys: one-time key number in the Merkle tree
            - n_parties: number of total parties
            - threshold_k: threshold value k

        @ return:
            - one k-of-n benchmark result
    """
    if total_keys <= 0:
        raise ValueError("total_keys must be positive")
    if n_parties <= 0:
        raise ValueError("n_parties must be positive")
    if threshold_k <= 0 or threshold_k > n_parties:
        raise ValueError("threshold_k must satisfy 1 <= k <= n_parties")

    t0 = now()
    _, parties, signer, verifier = build_kofn_system(
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
    )
    setup_time = now() - t0

    sign_times: list[float] = []
    verify_times: list[float] = []
    signature_sizes: list[int] = []
    success_count = 0

    # keep a deterministic coalition for repeatability
    selected_parties = parties[:threshold_k]

    for key_id in range(total_keys):
        message = f"kofn-message-{key_id}".encode()

        t1 = now()
        signed_data = signer.sign(
            message=message,
            keyid=key_id,
            parties=selected_parties,
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

    return KOfNRunResult(
        benchmark_name="kofn",
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
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



def benchmark_kofn(total_keys: int,
                   n_parties: int,
                   threshold_k: int,
                   repeats: int = 5) -> tuple[list[KOfNRunResult], KOfNBenchSummary]:
    """
        Run the k-of-n benchmark multiple times.
    """
    config = KOfNBenchConfig(
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
        repeats=repeats,
    )
    rows: list[KOfNRunResult] = []

    for repeat in range(config.repeats):
        row = run_kofn_once(
            total_keys=config.total_keys,
            n_parties=config.n_parties,
            threshold_k=config.threshold_k,
        )
        row.repeat = repeat
        rows.append(row)

    summary = KOfNBenchSummary(
        benchmark_name="kofn",
        total_keys=config.total_keys,
        n_parties=config.n_parties,
        threshold_k=config.threshold_k,
        repeats=config.repeats,

        setup_time_mean=sum(row.setup_time for row in rows) / config.repeats,
        success_rate_mean=sum(row.success_rate for row in rows) / config.repeats,
        avg_signature_size_mean=sum(row.avg_signature_size for row in rows) / config.repeats,
        sign_time_mean_mean=sum(row.sign_time_mean for row in rows) / config.repeats,
        verify_time_mean_mean=sum(row.verify_time_mean for row in rows) / config.repeats,
    )

    return rows, summary



def benchmark_kofn_by_k(total_keys: int,
                        n_parties: int,
                        k_values: list[int],
                        repeats: int = 5) -> list[KOfNRunResult]:
    """
        Run k-of-n benchmark while only changing threshold_k.
    """
    config = KOfNCompareConfig(
        total_keys=total_keys,
        n_parties=n_parties,
        k_values=k_values,
        repeats=repeats,
    )
    rows: list[KOfNRunResult] = []

    for threshold_k in config.k_values:
        for repeat in range(config.repeats):
            row = run_kofn_once(
                total_keys=config.total_keys,
                n_parties=config.n_parties,
                threshold_k=threshold_k,
            )
            row.repeat = repeat
            rows.append(row)

    return rows



def benchmark_kofn_failures(total_keys: int,
                            n_parties: int,
                            threshold_k: int) -> KOfNFailureResult:
    """
        Run correctness / rejection checks for the k-of-n extension.
    """
    _, parties, signer, verifier = build_kofn_system(
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
    )

    selected_parties = parties[:threshold_k]
    message = b"hello k-of-n threshold"
    key_id = 0

    signed_data = signer.sign(
        message=message,
        keyid=key_id,
        parties=selected_parties,
    )

    verify_correct = verifier.verify(message, signed_data)
    verify_wrong_message = verifier.verify(b"wrong message", signed_data)

    try:
        signer.sign(
            message=b"not enough parties",
            keyid=1,
            parties=parties[: threshold_k - 1],
        )
        less_than_k_rejected = False
    except ValueError:
        less_than_k_rejected = True

    try:
        signer.sign(
            message=b"reuse same subtree keyid",
            keyid=key_id,
            parties=selected_parties,
        )
        reuse_key_id_rejected = False
    except ValueError:
        reuse_key_id_rejected = True

    return KOfNFailureResult(
        benchmark_name="kofn_failure",
        total_keys=total_keys,
        n_parties=n_parties,
        threshold_k=threshold_k,
        verify_correct=bool(verify_correct),
        verify_wrong_message_rejected=not bool(verify_wrong_message),
        less_than_k_rejected=less_than_k_rejected,
        reuse_key_id_rejected=reuse_key_id_rejected,
    )