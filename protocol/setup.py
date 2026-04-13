# Threshold setup and XOR additive sharing for Lamport keys.

import secrets
from typing import Optional

from core.lamport_ots import LamportOTS
from core.merkle import MerkleTree
from .utils import (
    serialize_public_key,
    validate_lamport_key,
    validate_positive_int,
    validate_power_of_two,
    xor_many,
)


def xor_split_secret(secret: bytes, n_parties: int) -> list[bytes]:
    if not isinstance(secret, bytes):
        raise TypeError("secret must be bytes")
    validate_positive_int(n_parties, "n_parties")

    if n_parties == 1:
        return [secret]

    shares = [secrets.token_bytes(len(secret)) for _ in range(n_parties - 1)]
    final_share = xor_many(shares + [secret])
    shares.append(final_share)
    return shares


def share_lamport_private_key(private_key: dict, n_parties: int) -> list[dict]:
    validate_lamport_key(private_key, "private_key")
    validate_positive_int(n_parties, "n_parties")

    shares_by_party = [{"zero": [], "one": []} for _ in range(n_parties)]

    for label in ("zero", "one"):
        for secret in private_key[label]:
            secret_shares = xor_split_secret(secret, n_parties)
            for party_id, share in enumerate(secret_shares):
                shares_by_party[party_id][label].append(share)

    return shares_by_party


def setup_threshold_key_material(
    total_keys: int = 4,
    n_parties: int = 3,
    ots: Optional[LamportOTS] = None,
) -> tuple[dict, list[dict]]:
    validate_power_of_two(total_keys, "total_keys")
    validate_positive_int(n_parties, "n_parties")

    ots = ots or LamportOTS()
    public_keys = []
    party_key_shares = [[] for _ in range(n_parties)]

    for _ in range(total_keys):
        private_key, public_key = ots.keygen()
        public_keys.append(public_key)

        key_shares = share_lamport_private_key(private_key, n_parties)
        for party_id, key_share in enumerate(key_shares):
            party_key_shares[party_id].append(key_share)

    leaves = [serialize_public_key(public_key) for public_key in public_keys]
    merkle_tree = MerkleTree(leaves)
    auth_paths = [merkle_tree.get_auth_path(keyid) for keyid in range(total_keys)]

    public_params = {
        "scheme": "xor-n-of-n-lamport-hbs",
        "root": merkle_tree.root,
        "total_keys": total_keys,
        "n_parties": n_parties,
        "public_keys": public_keys,
        "auth_paths": auth_paths,
    }

    party_share_bundles = [
        {
            "party_id": party_id,
            "n_parties": n_parties,
            "total_keys": total_keys,
            "key_shares": party_key_shares[party_id],
        }
        for party_id in range(n_parties)
    ]

    return public_params, party_share_bundles
