from entities.party import Party
from entities.trusted_server import TrustedServer
from entities.untrusted_server import UntrustedServer
from entities.verifier import Verifier

from benchmark.src.utils.metrics import digest32, serialized_size

# timing
from benchmark.src.utils.timer import now, summarize_time_measure

# datatypes
from benchmark.src.datatypes.all_cfgs_dt import thresholdBench_cfgDt
from benchmark.src.datatypes.all_result_dt import thresholdRun_resultDt
from benchmark.src.datatypes.all_summary_dt import thresholdBench_sumDt



def build_threshold_system(total_keys: int,
                           n_parties: int):
      
    trusted_server = TrustedServer(total_keys = total_keys,
                                   n_parties = n_parties)
    public_params, share_bundles = trusted_server.setup()

    parties = [
        Party(
            party_id = bundle["party_id"],
            share_bundle = bundle,
        )
        for bundle in share_bundles
    ]

    signer = UntrustedServer(public_params = public_params)
    verifier = Verifier(root = public_params["root"],
                        total_keys = public_params["total_keys"])

    return public_params, parties, signer, verifier



def run_threshold_once(total_keys: int,
                       n_parties: int) -> thresholdRun_resultDt:
    """
        threshold hbs
    """

    t0 = now()
    public_params, parties, signer, verifier = build_threshold_system(
        total_keys = total_keys,
        n_parties = n_parties,
    )
    setup_time = now() - t0

    sign_times: list[float] = []
    verify_times: list[float] = []
    signature_sizes: list[int] = []
    path_lengths: list[int] = []
    success_count = 0

    for key_id in range(total_keys):
        message = digest32(f"threshold-message-{key_id}".encode())

        t1 = now()
        signed_data = signer.sign(
            message = message,
            keyid = key_id,
            parties = parties,
        )
        sign_times.append(now() - t1)

        signature_sizes.append(serialized_size(signed_data))
        path_lengths.append(len(signed_data["path"]))

        t2 = now()
        ok = verifier.verify(message, signed_data)
        verify_times.append(now() - t2)

        if ok:
            success_count += 1

    # Step 3: summarize the timing lists.
    sign_stats = summarize_time_measure(sign_times)
    verify_stats = summarize_time_measure(verify_times)

    return thresholdRun_resultDt(
        benchmark_name = "threshold",

        total_keys = total_keys,
        n_parties = n_parties,
        setup_time = setup_time,
        success_rate = success_count / total_keys,

        avg_signature_size = sum(signature_sizes) / len(signature_sizes),
        avg_path_length = sum(path_lengths) / len(path_lengths),
        root_size = len(public_params["root"]),

        sign_time_mean = sign_stats.mean,
        sign_time_stdev = sign_stats.stdev,
        sign_time_min = sign_stats.min_value,
        sign_time_max = sign_stats.max_value,

        verify_time_mean = verify_stats.mean,
        verify_time_stdev = verify_stats.stdev,
        verify_time_min = verify_stats.min_value,
        verify_time_max = verify_stats.max_value,
    )



def benchmark_threshold(total_keys: int,
                        n_parties: int,
                        repeats: int = 5) -> tuple[list[thresholdRun_resultDt], thresholdBench_sumDt]:

    CONFIG = thresholdBench_cfgDt(total_keys = total_keys,
                                  n_parties = n_parties,
                                  repeats = repeats)
    rows: list[thresholdRun_resultDt] = []

    # repeat
    for repeat in range(CONFIG.repeats):
        row = run_threshold_once(total_keys = CONFIG.total_keys,
                                 n_parties = CONFIG.n_parties)
        row.repeat = repeat
        rows.append(row)

    summary = thresholdBench_sumDt(
        benchmark_name = "threshold",

        total_keys = CONFIG.total_keys,
        n_parties = CONFIG.n_parties,
        repeats = CONFIG.repeats,

        setup_time_mean = sum(row.setup_time for row in rows) / CONFIG.repeats,
        success_rate_mean = sum(row.success_rate for row in rows) / CONFIG.repeats,
        avg_signature_size_mean = sum(row.avg_signature_size for row in rows) / CONFIG.repeats,
        avg_path_length_mean = sum(row.avg_path_length for row in rows) / CONFIG.repeats,
        sign_time_mean_mean = sum(row.sign_time_mean for row in rows) / CONFIG.repeats,
        verify_time_mean_mean = sum(row.verify_time_mean for row in rows) / CONFIG.repeats,
    )

    return rows, summary