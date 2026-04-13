# Trusted dealer for threshold HBS setup.

from core.lamport_ots import LamportOTS
from protocol.setup import setup_threshold_key_material


class TrustedServer:
    def __init__(self, total_keys: int = 4, n_parties: int = 3):
        self.total_keys = total_keys
        self.n_parties = n_parties
        self.ots = LamportOTS()
        self.public_params = None
        self.party_share_bundles = None

    def setup(self) -> tuple[dict, list[dict]]:
        public_params, party_share_bundles = setup_threshold_key_material(
            total_keys=self.total_keys,
            n_parties=self.n_parties,
            ots=self.ots,
        )
        self.public_params = public_params
        self.party_share_bundles = party_share_bundles
        return public_params, party_share_bundles
