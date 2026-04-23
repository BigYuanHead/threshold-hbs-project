from dataclasses import asdict, dataclass

# timing
from benchmark.src.datatypes.utils_dt import TimeStats
from benchmark.src.utils.timer import now, timed, summarize_time_measure

from benchmark.src.utils.metrics import serialized_size
from benchmark.src.utils.timer import now
from extension_3.batch_threshold import BatchThresholdHBS

from entities.party import Party
from entities.trusted_server import TrustedServer
from entities.untrusted_server import UntrustedServer
from entities.verifier import Verifier

# datatypes
from benchmark.src.datatypes.all_cfgs_dt import BatchBenchConfig
from benchmark.src.datatypes.all_result_dt import BatchFailureResult, BatchRunResult, NonBatchRunResult


def build_threshold_system(total_keys: int,
                           n_parties: int) -> tuple[dict,
                                                    list[Party],
                                                    UntrustedServer,
                                                    Verifier
                                                ]:
    """
        setup the threshold system

        @ input:
            - total_keys: onetime key num
            - n_parties: threshold parties num

    """

    trusted_server = TrustedServer(total_keys=total_keys,
                                   n_parties=n_parties)
    public_params, share_bundles = trusted_server.setup()

    parties = [ Party(
                    party_id = bundle["party_id"],
                    share_bundle = bundle,
                )
                for bundle in share_bundles
    ]

    signer = UntrustedServer(public_params = public_params)
    verifier = Verifier(root = public_params["root"],
                        total_keys = public_params["total_keys"])

    return public_params, parties, signer, verifier



def make_messages(batch_size: int,
                  prefix: str = "batch_msg") -> list[bytes]:
    """
        fake msg generator
    """
    return [f"{prefix}-{index}".encode() for index in range(batch_size)]




def run_batch_once(total_keys: int,
                   n_parties: int,
                   batch_size: int,
                   key_id: int = 0) -> BatchRunResult:
    """
        run batch threshold benchmark once

        @ input:
            - total_keys: onetime keys num
            - n_parties: threshold party num
            - batch_size: msg num in one batch
            - key_id: signing key id used for the batch root
            
    """


    _, parties, signer, verifier = build_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )

    batch_hbs = BatchThresholdHBS(signer=signer, verifier=verifier)
    messages = make_messages(batch_size, prefix="batch_msg")

    t1 = now()
    batch_pack = batch_hbs.batch_sign(
        messages=messages,
        keyid=key_id,
        parties=parties,
    )
    batch_sign_time = now() - t1

    verify_times: list[float] = []
    success_count = 0

    for index, message in enumerate(messages):
        t2 = now()
        ok = batch_hbs.batch_verify(message, index, batch_pack)
        verify_times.append(now() - t2)

        if ok:
            success_count += 1

    total_batch_verify_time = sum(verify_times)
    verify_stats = summarize_time_measure(verify_times)

    return BatchRunResult(
        benchmark_name = "batch_threshold",
        total_keys = total_keys,
        n_parties = n_parties,
        batch_size = batch_size,

        batch_sign_time = batch_sign_time,
        total_batch_verify_time = total_batch_verify_time,
        per_message_sign_time = batch_sign_time / batch_size,
        per_message_verify_time = total_batch_verify_time / batch_size,
        batch_pack_size = serialized_size(batch_pack),
        success_rate = success_count / batch_size,

        # time
        verify_time_mean = verify_stats.mean,
        verify_time_stdev = verify_stats.stdev,
        verify_time_min = verify_stats.min_value,
        verify_time_max = verify_stats.max_value,
    )


def benchmark_batch_by_size(total_keys: int,
                            n_parties: int,
                            batch_sizes: list[int],
                            repeats: int) -> list[BatchRunResult]:
    """
        test batch under different batch size
    """
    rows: list[BatchRunResult] = []

    for batch_size in batch_sizes:
        config = BatchBenchConfig(
            total_keys = total_keys,
            n_parties = n_parties,
            batch_size = batch_size,
            repeats = repeats,
            key_id = 0,
        )

        for repeat in range(config.repeats):
            row = run_batch_once(
                total_keys = config.total_keys,
                n_parties = config.n_parties,
                batch_size = config.batch_size,
                key_id = config.key_id,
            )
            row.repeat = repeat
            rows.append(row)

    return rows


def run_nonbatch_once(total_keys: int,
                      n_parties: int,
                      message_count: int) -> NonBatchRunResult:
    """
        run the non batch threshold bench once

        @ input:
            ...
    """

    _, parties, signer, verifier = build_threshold_system(
        total_keys=total_keys,
        n_parties=n_parties,
    )

    messages = make_messages(message_count, prefix="nonbatch_msg")

    # collect output
    sign_times: list[float] = []
    verify_times: list[float] = []
    total_size = 0
    success_count = 0

    for key_id, message in enumerate(messages):
        t1 = now()
        signed_data = signer.sign(
            message=message,
            keyid=key_id,
            parties=parties,
        )
        sign_times.append(now() - t1)
        total_size += serialized_size(signed_data)

        t2 = now()
        ok = verifier.verify(message, signed_data)
        verify_times.append(now() - t2)

        if ok:
            success_count += 1

    total_sign_time = sum(sign_times)
    total_verify_time = sum(verify_times)

    sign_stats = summarize_time_measure(sign_times)
    verify_stats = summarize_time_measure(verify_times)

    return NonBatchRunResult(
        benchmark_name = "nonbatch_threshold",
        total_keys = total_keys,
        n_parties = n_parties,
        message_count = message_count,

        total_sign_time = total_sign_time,
        total_verify_time = total_verify_time,
        per_message_sign_time = total_sign_time / message_count,
        per_message_verify_time = total_verify_time / message_count,
        total_output_size = total_size,
        success_rate = success_count / message_count,

        # sign
        sign_time_mean=sign_stats.mean,
        sign_time_stdev=sign_stats.stdev,
        sign_time_min=sign_stats.min_value,
        sign_time_max=sign_stats.max_value,
        # verify
        verify_time_mean=verify_stats.mean,
        verify_time_stdev=verify_stats.stdev,
        verify_time_min=verify_stats.min_value,
        verify_time_max=verify_stats.max_value,
    )


def compare_batch_vs_nonbatch(total_keys: int,
                              n_parties: int,
                              message_count: int,
                              repeats: int = 5) -> list[BatchRunResult | NonBatchRunResult]:
    """
        compare batch and nonbatch
    """
    rows: list[BatchRunResult | NonBatchRunResult] = []

    for repeat in range(repeats):
        non_batch_row = run_nonbatch_once(
            total_keys=total_keys,
            n_parties=n_parties,
            message_count=message_count,
        )
        non_batch_row.repeat = repeat
        rows.append(non_batch_row)

        batch_row = run_batch_once(
            total_keys=total_keys,
            n_parties=n_parties,
            batch_size=message_count,
            key_id=0,
        )
        batch_row.repeat = repeat
        rows.append(batch_row)

    return rows


def benchmark_batch_failures(total_keys: int,
                             n_parties: int,
                             batch_size: int) -> BatchFailureResult:
    """
       batch extension method correctness and rejection checks
    """
    _, parties, signer, verifier = build_threshold_system(
        total_keys = total_keys,
        n_parties = n_parties,
    )

    # instant batch threshold hbs
    batch_hbs = BatchThresholdHBS(signer = signer, verifier = verifier)
    messages = make_messages(batch_size)
    batch_pack = batch_hbs.batch_sign(messages = messages,
                                      keyid = 0,
                                      parties=parties)
    
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

    return BatchFailureResult(
        benchmark_name = "batch_failure",
        total_keys = total_keys,
        n_parties = n_parties,
        batch_size = batch_size,

        verify_correct = bool(verify_correct),
        verify_wrong_message_rejected = not bool(verify_wrong_message),
        verify_wrong_index_rejected = not bool(verify_wrong_index),
        verify_wrong_path_rejected = not bool(verify_wrong_path),
    )