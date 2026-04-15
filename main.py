# End-to-end demo for the minimal threshold HBS workflow.

from entities import Party, TrustedServer, UntrustedServer, Verifier
from benchmark.run_benchmarks import benchmark_main

def run_demo() -> bool:
    total_keys = 4
    n_parties = 3
    keyid = 0
    message = b"hello threshold hbs"

    trusted_server = TrustedServer(total_keys=total_keys, n_parties=n_parties)
    public_params, party_share_bundles = trusted_server.setup()

    parties = [
        Party(party_id=bundle["party_id"], share_bundle=bundle)
        for bundle in party_share_bundles
    ]

    untrusted_server = UntrustedServer(public_params)
    signed_data = untrusted_server.sign(message=message, keyid=keyid, parties=parties)

    verifier = Verifier(root=public_params["root"], total_keys=public_params["total_keys"])
    verified = verifier.verify(message, signed_data)

    print("Threshold HBS demo")
    print(f"parties: {n_parties}-of-{n_parties}")
    print(f"keyid: {keyid}")
    print(f"root: {public_params['root'].hex()}")
    print(f"verified: {verified}")

    return verified

def run_benchmark():
    benchmark_main()



if __name__ == "__main__":
    # run_demo()
    run_benchmark()
