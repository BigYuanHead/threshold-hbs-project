from extension_1.kofn_setup import setup_kofn_key_material
from extension_1.kofn_party import KOfNParty
from extension_1.kofn_server import KOfNUntrustedServer
from extension_1.kofn_verifier import KOfNVerifier


def main():
    total_keys = 4
    n_parties = 4
    threshold_k = 3
    keyid = 0
    message = b"hello k-of-n threshold"

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

    selected_parties = [parties[0], parties[1], parties[3]]
    signed_data = signer.sign(
        message=message,
        keyid=keyid,
        parties=selected_parties,
    )

    print("signed_data fields:", sorted(signed_data.keys()))
    print("selected party ids:", signed_data["party_ids"])
    print("subtree id:", signed_data["subtree_id"])
    print("verify correct:", verifier.verify(message, signed_data))
    print("verify wrong message:", verifier.verify(b"wrong message", signed_data))

    try:
        signer.sign(
            message=b"not enough parties",
            keyid=1,
            parties=[parties[0], parties[1]],
        )
        print("less than k rejected: False")
    except ValueError:
        print("less than k rejected: True")

    try:
        signer.sign(
            message=b"reuse same subtree keyid",
            keyid=keyid,
            parties=selected_parties,
        )
        print("reuse keyid rejected: False")
    except ValueError:
        print("reuse keyid rejected: True")


if __name__ == "__main__":
    main()
