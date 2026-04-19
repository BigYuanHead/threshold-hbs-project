from itertools import combinations
from typing import Optional

from core.lamport_ots import LamportOTS
from core.merkle import MerkleTree
from protocol.setup import share_lamport_private_key
from protocol.utils import (
    serialize_public_key,
    validate_positive_int,
    validate_power_of_two,
)


def _next_power_of_two(value):
    validate_positive_int(value, "value")
    power = 1
    while power < value:
        power *= 2
    return power


def setup_kofn_key_material(
    total_keys=4,
    n_parties=4,
    threshold_k=3,
    ots: Optional[LamportOTS] = None,
):
    validate_power_of_two(total_keys, "total_keys")
    validate_positive_int(n_parties, "n_parties")
    validate_positive_int(threshold_k, "threshold_k")
    if threshold_k > n_parties:
        raise ValueError("threshold_k cannot be greater than n_parties")

    ots = ots or LamportOTS()
    subsets = [tuple(group) for group in combinations(range(n_parties), threshold_k)]
    party_subset_shares = [{} for _ in range(n_parties)]
    subtrees = []

    for subset_id, party_ids in enumerate(subsets):
        public_keys = []
        subtree_party_shares = [[] for _ in range(threshold_k)]

        for _ in range(total_keys):
            private_key, public_key = ots.keygen()
            public_keys.append(public_key)

            key_shares = share_lamport_private_key(private_key, threshold_k)
            for member_index, key_share in enumerate(key_shares):
                subtree_party_shares[member_index].append(key_share)

        leaves = [serialize_public_key(public_key) for public_key in public_keys]
        merkle_tree = MerkleTree(leaves)
        auth_paths = [merkle_tree.get_auth_path(keyid) for keyid in range(total_keys)]

        subtrees.append(
            {
                "subset_id": subset_id,
                "party_ids": list(party_ids),
                "root": merkle_tree.root,
                "total_keys": total_keys,
                "public_keys": public_keys,
                "auth_paths": auth_paths,
            }
        )

        for member_index, party_id in enumerate(party_ids):
            party_subset_shares[party_id][subset_id] = {
                "subset_id": subset_id,
                "party_ids": list(party_ids),
                "key_shares": subtree_party_shares[member_index],
            }

    global_leaves = [subtree["root"] for subtree in subtrees]
    padded_leaf_count = _next_power_of_two(len(global_leaves))
    while len(global_leaves) < padded_leaf_count:
        global_leaves.append(global_leaves[-1])

    global_tree = MerkleTree(global_leaves)
    for subtree in subtrees:
        subtree["subtree_path"] = global_tree.get_auth_path(subtree["subset_id"])

    public_params = {
        "scheme": "k-of-n-subtree-lamport-hbs",
        "root": global_tree.root,
        "total_keys": total_keys,
        "n_parties": n_parties,
        "threshold_k": threshold_k,
        "subtrees": subtrees,
        "subset_count": len(subsets),
        "padded_subset_count": padded_leaf_count,
    }

    party_share_bundles = [
        {
            "party_id": party_id,
            "n_parties": n_parties,
            "threshold_k": threshold_k,
            "total_keys": total_keys,
            "subset_shares": party_subset_shares[party_id],
        }
        for party_id in range(n_parties)
    ]

    return public_params, party_share_bundles
