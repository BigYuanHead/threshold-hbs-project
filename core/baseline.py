from .lamport_ots import LamportOTS
from .merkle import MerkleTree

# Stateful Hash-Based Signature (HBS) implementation
class StatefulHBS:
    # Initialize the HBS with a specified number of keys
    def __init__(self, total_keys=4):
        # error check for total_keys
        if not isinstance(total_keys, int):
            raise TypeError("total_keys must be an integer")
        if total_keys <= 0:
            raise ValueError("total_keys must be a positive integer")
        if total_keys & (total_keys - 1) != 0:
            raise ValueError("total_keys must be a power of 2")
        self.total_keys = total_keys
        self.ots = LamportOTS()

        self.private_keys = []
        self.public_keys = []
        self.used_keyids = set()

        for _ in range(total_keys):
            secret_k, public_k = self.ots.keygen()
            self.private_keys.append(secret_k)
            self.public_keys.append(public_k)

        leaves = [self.serialize_public_key(pk) for pk in self.public_keys]
        self.merkle_tree = MerkleTree(leaves)
        self.root = self.merkle_tree.root

    # Serialize a public key into bytes for Merkle Tree leaves
    def serialize_public_key(self, public_key):
        if not isinstance(public_key, dict):
            raise TypeError("public_key must be a dict")
        if "zero" not in public_key or "one" not in public_key:
            raise ValueError("public_key must contain zero and one")
        serial_key = b"".join(public_key["zero"] + public_key["one"])
        return serial_key

    # Sign a message using a specific keyid
    def sign(self, keyid, message: bytes) -> dict:
        # error check
        if not isinstance(keyid, int):
            raise TypeError("keyid must be an integer")
        if keyid < 0 or keyid >= self.total_keys:
            raise ValueError("keyid out of range")
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if keyid in self.used_keyids:
            raise ValueError("Keyid has already been used")

        private_key = self.private_keys[keyid]
        signature = self.ots.sign(message, private_key)
        path = self.merkle_tree.get_auth_path(keyid)

        self.used_keyids.add(keyid)

        return {
            "keyid": keyid,
            "signature": signature,
            "path": path,
        }

    # Verify a signature for a given message and signed data
    def verify(self, message: bytes, signed_data) -> bool:
        # error check
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if not isinstance(signed_data, dict):
            raise TypeError("signed_data must be a dict")
        if "keyid" not in signed_data or "signature" not in signed_data or "path" not in signed_data:
            return False
        
        if not isinstance(signed_data["keyid"], int):
            return False
        if signed_data["keyid"] < 0 or signed_data["keyid"] >= self.total_keys:
            return False
        
        keyid = signed_data["keyid"]
        signature = signed_data["signature"]
        path = signed_data["path"]

        public_key = self.public_keys[keyid]

        if not self.ots.verify(message, signature, public_key):
            return False

        leaf = self.serialize_public_key(public_key)
        return self.merkle_tree.verify_path(leaf, keyid, path, self.root)

