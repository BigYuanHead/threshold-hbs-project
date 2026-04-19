import unittest

from extension_1 import (
    KOfNParty,
    KOfNUntrustedServer,
    KOfNVerifier,
    setup_kofn_key_material,
    verify_kofn_signature,
)


class TestExtension1KOfN(unittest.TestCase):
    def setUp(self):
        self.public_params, bundles = setup_kofn_key_material(
            total_keys=4,
            n_parties=4,
            threshold_k=3,
        )
        self.parties = [
            KOfNParty(party_id=bundle["party_id"], share_bundle=bundle)
            for bundle in bundles
        ]
        self.signer = KOfNUntrustedServer(self.public_params)
        self.verifier = KOfNVerifier(
            root=self.public_params["root"],
            total_keys=self.public_params["total_keys"],
        )

    def test_any_valid_k_party_group_can_sign(self):
        message = b"k-of-n threshold message"
        signed_data = self.signer.sign(
            message=message,
            keyid=0,
            parties=[self.parties[0], self.parties[2], self.parties[3]],
        )

        self.assertEqual(signed_data["party_ids"], [0, 2, 3])
        self.assertIn("keyid", signed_data)
        self.assertIn("public_key", signed_data)
        self.assertIn("signature", signed_data)
        self.assertIn("path", signed_data)
        self.assertTrue(self.verifier.verify(message, signed_data))
        self.assertTrue(
            verify_kofn_signature(
                message,
                signed_data,
                self.public_params["root"],
                total_keys=self.public_params["total_keys"],
            )
        )

    def test_less_than_k_parties_cannot_sign(self):
        with self.assertRaises(ValueError):
            self.signer.sign(
                message=b"not enough parties",
                keyid=0,
                parties=[self.parties[0], self.parties[1]],
            )

    def test_wrong_message_fails_verification(self):
        signed_data = self.signer.sign(
            message=b"correct message",
            keyid=1,
            parties=[self.parties[0], self.parties[1], self.parties[2]],
        )

        self.assertFalse(self.verifier.verify(b"wrong message", signed_data))

    def test_reusing_keyid_in_same_subtree_is_rejected(self):
        selected_parties = [self.parties[1], self.parties[2], self.parties[3]]
        self.signer.sign(
            message=b"first message",
            keyid=2,
            parties=selected_parties,
        )

        with self.assertRaises(ValueError):
            self.signer.sign(
                message=b"second message",
                keyid=2,
                parties=selected_parties,
            )


if __name__ == "__main__":
    unittest.main()
