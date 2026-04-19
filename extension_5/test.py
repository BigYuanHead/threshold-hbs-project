from extension_5.winternitz_standardized import WinternitzStandardized
from extension_5.wz_setup import setup_winternitz_key_material
from extension_5.wz_party import WinternitzParty
from extension_5.wz_server import WinternitzUntrustedServer
from extension_5.wz_verifier import WinternitzVerifier


def main():
    backend = WinternitzStandardized(w=16)

    total_keys = 4
    n_parties = 3
    keyid = 0
    message = b"hello winternitz threshold"

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

    signed_data = signer.sign(
        message=message,
        keyid=keyid,
        parties=parties,
    )

    print("signed_data fields:", sorted(signed_data.keys()))
    print("signature length:", len(signed_data["signature"]))
    print("public key length:", len(signed_data["public_key"]["chains"]))

    print("verify correct:", verifier.verify(message, signed_data))
    print("verify wrong message:", verifier.verify(b"wrong message", signed_data))

    bad_signed_data = signed_data.copy()
    bad_signature = signed_data["signature"].copy()
    bad_signature[0] = b"wrong"
    bad_signed_data["signature"] = bad_signature

    print("verify wrong signature:", verifier.verify(message, bad_signed_data))

    try:
        signer.sign(
            message=b"second message",
            keyid=keyid,
            parties=parties,
        )
        print("reuse keyid: False")
    except ValueError:
        print("reuse keyid: True")


if __name__ == "__main__":
    main()