from benchmark.src.utils.metrics import serialized_size

# timing
from benchmark.src.utils.timer import now, summarize_time_measure

# extension 1 libraries
from extension_1.kofn_setup import setup_kofn_key_material
from extension_1.kofn_party import KOfNParty
from extension_1.kofn_server import KOfNUntrustedServer
from extension_1.kofn_verifier import KOfNVerifier

# datatypes
from benchmark.src.datatypes.all_summary_dt import KOfNBench_sumDt
from benchmark.src.datatypes.all_cfgs_dt import KOfNBench_cfgDt, KOfNCompare_cfgDt
from benchmark.src.datatypes.all_result_dt import KOfNRun_resultDt, KOfNFailure_resultDt



def build_kofn_system(total_keys: int,
                      n_parties: int,
                      threshold_k: int):
    """
        @ input:
            - total_keys: one time key num
            - n_parties: total party num
            - threshold_k: threshold value

        @ return:
            - public_params
            - parties
            - signer
            - verifier
    """
    public_params, party_share_bundles = setup_kofn_key_material(
        total_keys = total_keys,
        n_parties = n_parties,
        threshold_k = threshold_k,
    )

    parties = [
        KOfNParty(
            party_id = bundle["party_id"],
            share_bundle = bundle,
        )
        for bundle in party_share_bundles
    ]

    signer = KOfNUntrustedServer(public_params)
    verifier = KOfNVerifier(
        root = public_params["root"],
        total_keys = public_params["total_keys"],
    )

    return public_params, parties, signer, verifier



def run_kofn_once(total_keys: int,
                  n_parties: int,
                  threshold_k: int) -> KOfNRun_resultDt:
    """
        k of n threshold nbs

    """

    t0 = now()
    _, parties, signer, verifier = build_kofn_system(
        total_keys = total_keys,
        n_parties = n_parties,
        threshold_k = threshold_k,
    )
    setup_time = now() - t0

    # get result
    sign_times: list[float] = []
    verify_times: list[float] = []
    signature_sizes: list[int] = []
    success_count = 0

    # keep one determin coalition for repeat
    selected_parties = parties[:threshold_k]

    for key_id in range(total_keys):
        message = f"kofn-message-{key_id}".encode()

        t1 = now()
        signed_data = signer.sign(
            message = message,
            keyid = key_id,
            parties = selected_parties,
        )
        sign_times.append(now() - t1)

        signature_sizes.append(serialized_size(signed_data))

        t2 = now()
        ok = verifier.verify(message, signed_data)
        verify_times.append(now() - t2)

        if ok:
            success_count += 1

    # Step 3: summarize the timing lists.
    sign_stats = summarize_time_measure(sign_times)
    verify_stats = summarize_time_measure(verify_times)

    return KOfNRun_resultDt(
        benchmark_name = "kofn",
        total_keys = total_keys,

        n_parties = n_parties,
        threshold_k = threshold_k,

        setup_time = setup_time,
        success_rate = success_count / total_keys,
        avg_signature_size = sum(signature_sizes) / len(signature_sizes),

        sign_time_mean = sign_stats.mean,
        sign_time_stdev = sign_stats.stdev,
        sign_time_min = sign_stats.min_value,
        sign_time_max = sign_stats.max_value,

        verify_time_mean = verify_stats.mean,
        verify_time_stdev = verify_stats.stdev,
        verify_time_min = verify_stats.min_value,
        verify_time_max = verify_stats.max_value,
    )



def benchmark_kofn(total_keys: int,
                   n_parties: int,
                   threshold_k: int,
                   repeats: int = 5) -> tuple[list[KOfNRun_resultDt], KOfNBench_sumDt]:
    """
        repeat run
    """
   
    CONFIG = KOfNBench_cfgDt(
        total_keys = total_keys,
        n_parties = n_parties,
        threshold_k = threshold_k,
        repeats = repeats,
    )
    rows: list[KOfNRun_resultDt] = []

    # Step 1: run the same experiment several times.
    for repeat in range(CONFIG.repeats):
        row = run_kofn_once(
            total_keys = CONFIG.total_keys,
            n_parties = CONFIG.n_parties,
            threshold_k = CONFIG.threshold_k,
        )
        row.repeat = repeat
        rows.append(row)

    # Step 2: build one simple summary object.
    summary = KOfNBench_sumDt(
        benchmark_name = "kofn",
        total_keys = CONFIG.total_keys,
        n_parties = CONFIG.n_parties,
        threshold_k = CONFIG.threshold_k,
        repeats = CONFIG.repeats,
        setup_time_mean = sum(row.setup_time for row in rows) / CONFIG.repeats,
        success_rate_mean = sum(row.success_rate for row in rows) / CONFIG.repeats,
        avg_signature_size_mean = sum(row.avg_signature_size for row in rows) / CONFIG.repeats,
        sign_time_mean_mean = sum(row.sign_time_mean for row in rows) / CONFIG.repeats,
        verify_time_mean_mean = sum(row.verify_time_mean for row in rows) / CONFIG.repeats,
    )

    return rows, summary



def benchmark_kofn_by_k(total_keys: int,
                        n_parties: int,
                        k_values: list[int],
                        repeats: int = 5) -> list[KOfNRun_resultDt]:
    """
        only change threshold k.
    """

    CONFIG = KOfNCompare_cfgDt(
        total_keys = total_keys,
        n_parties = n_parties,
        k_values = k_values,
        repeats = repeats,
    )
    rows: list[KOfNRun_resultDt] = []

    # Run one benchmark group for each k value.
    for threshold_k in CONFIG.k_values:
        for repeat in range(CONFIG.repeats):
            row = run_kofn_once(
                total_keys = CONFIG.total_keys,
                n_parties = CONFIG.n_parties,
                threshold_k = threshold_k,
            )
            row.repeat = repeat
            rows.append(row)

    return rows



def benchmark_kofn_failures(total_keys: int,
                            n_parties: int,
                            threshold_k: int) -> KOfNFailure_resultDt:
    """
        Run correctness and rejection checks for the k-of-n extension.
    """

    _, parties, signer, verifier = build_kofn_system(
        total_keys = total_keys,
        n_parties = n_parties,
        threshold_k = threshold_k,
    )

    selected_parties = parties[:threshold_k]
    message = b"COMP6453 hello kofn threshold"
    key_id = 0

    signed_data = signer.sign(
        message = message,
        keyid = key_id,
        parties = selected_parties,
    )

    verify_correct = verifier.verify(message, signed_data)
    verify_wrong_message = verifier.verify(b"wrong message", signed_data)

    try:
        signer.sign(
            message = b"not enough parties",
            keyid = 1,
            parties = parties[: threshold_k - 1],
        )
        less_than_k_rejected = False
    except ValueError:
        less_than_k_rejected = True

    try:
        signer.sign(
            message = b"reuse same subtree keyid",
            keyid = key_id,
            parties = selected_parties,
        )
        reuse_key_id_rejected = False
    except ValueError:
        reuse_key_id_rejected = True

    return KOfNFailure_resultDt(
        benchmark_name = "kofn_failure",
        total_keys = total_keys,
        n_parties = n_parties,
        threshold_k = threshold_k,
        verify_correct = bool(verify_correct),
        verify_wrong_message_rejected = not bool(verify_wrong_message),
        less_than_k_rejected = less_than_k_rejected,
        reuse_key_id_rejected = reuse_key_id_rejected,
    )