# Tests for the minimal n-of-n threshold HBS workflow.

import unittest

from core.lamport_ots import LamportOTS
from entities import Party, TrustedServer, UntrustedServer, Verifier
from protocol.setup import share_lamport_private_key
from protocol.utils import xor_many


class TestThresholdEndToEnd(unittest.TestCase):
    def test_xor_shares_reconstruct_lamport_private_key(self):
        private_key, _ = LamportOTS().keygen()
        shares = share_lamport_private_key(private_key, n_parties=3)

        for label in ("zero", "one"):
            for index, secret in enumerate(private_key[label]):
                reconstructed = xor_many([party_share[label][index] for party_share in shares])
                self.assertEqual(reconstructed, secret)

    def test_threshold_sign_and_verify(self):
        trusted_server = TrustedServer(total_keys=4, n_parties=3)
        public_params, party_share_bundles = trusted_server.setup()

        parties = [
            Party(party_id=bundle["party_id"], share_bundle=bundle)
            for bundle in party_share_bundles
        ]
        untrusted_server = UntrustedServer(public_params)
        verifier = Verifier(
            root=public_params["root"],
            total_keys=public_params["total_keys"],
        )

        message = b"threshold hbs test message"
        signed_data = untrusted_server.sign(message=message, keyid=0, parties=parties)

        self.assertTrue(verifier.verify(message, signed_data))
        self.assertFalse(verifier.verify(b"wrong message", signed_data))

    def test_party_refuses_reused_keyid(self):
        trusted_server = TrustedServer(total_keys=4, n_parties=3)
        public_params, party_share_bundles = trusted_server.setup()
        parties = [
            Party(party_id=bundle["party_id"], share_bundle=bundle)
            for bundle in party_share_bundles
        ]
        untrusted_server = UntrustedServer(public_params)

        message = b"first message"
        untrusted_server.sign(message=message, keyid=0, parties=parties)

        with self.assertRaises(ValueError):
            untrusted_server.sign(message=b"second message", keyid=0, parties=parties)


if __name__ == "__main__":
    unittest.main()
