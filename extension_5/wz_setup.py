from core.merkle import MerkleTree
from extension_5.winternitz_standardized import WinternitzStandardized

# setup
def setup_winternitz_key_material(total_keys=4, n_parties=3, backend=None):
    if not isinstance(total_keys, int):
        raise TypeError("total_keys must be an integer")
    if total_keys <= 0:
        raise ValueError("total_keys must be positive")
    if total_keys & (total_keys - 1) != 0:
        raise ValueError("total_keys must be a power of 2")
    if not isinstance(n_parties, int):
        raise TypeError("n_parties must be an integer")
    if n_parties <= 0:
        raise ValueError("n_parties must be positive")

    backend = backend or WinternitzStandardized(w=16)
    p_keys = []
    party_key_shares = [[] for _ in range(n_parties)]

    for _ in range(total_keys):
        private_key, public_key = backend.keygen()
        p_keys.append(public_key)
        key_shares = backend.share_private_key(private_key, n_parties)

        for party_id, key_share in enumerate(key_shares):
            party_key_shares[party_id].append(key_share)

    leaves = [
        backend.serialize_public_key(public_key)
        for public_key in p_keys
    ]
    # create merkle tree
    merkle_tree = MerkleTree(leaves)

    auth_paths = [
        merkle_tree.get_auth_path(keyid)
        for keyid in range(total_keys)
    ]
    # parameters
    public_params = {
        "scheme": "winternitz-threshold-hbs",
        "root": merkle_tree.root,
        "total_keys": total_keys,
        "n_parties": n_parties,
        "public_keys": p_keys,
        "auth_paths": auth_paths,
        "w": backend.w,
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