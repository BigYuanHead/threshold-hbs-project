from .lamport_ots import LamportOTS
from .merkle import MerkleTree

# Stateful Hash-Based Signature (HBS) implementation
class StatefulHBS:
    # Initialize the HBS with a specified number of keys
    def __init__(self, total_keys=4):
        self.total_keys = total_keys
        self.ots = LamportOTS()

        self.private_keys = []
        self.public_keys = []
        self.used_keyids = set()

        for _ in range(total_keys):
            sk, pk = self.ots.keygen()
            self.private_keys.append(sk)
            self.public_keys.append(pk)

        leaves = [self.serialize_public_key(pk) for pk in self.public_keys]
        self.merkle_tree = MerkleTree(leaves)
        self.root = self.merkle_tree.root

    # Serialize a public key into bytes for Merkle Tree leaves
    def serialize_public_key(self, public_key):
        return b"".join(public_key["zero"] + public_key["one"])

    # Sign a message using a specific keyid
    def sign(self, keyid, message: bytes):
        if keyid in self.used_keyids:
            raise ValueError("This keyid has already been used")

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
        keyid = signed_data["keyid"]
        signature = signed_data["signature"]
        path = signed_data["path"]

        public_key = self.public_keys[keyid]

        if not self.ots.verify(message, signature, public_key):
            return False

        leaf = self.serialize_public_key(public_key)
        return MerkleTree.verify_path(leaf, keyid, path, self.root)

# Test the Stateful HBS implementation
'''
if __name__ == "__main__":
    print("Testing stateful_hbs.py...")

    hbs = StatefulHBS(total_keys=4)
    msg = b"hello stateful signatures"

    signed = hbs.sign(0, msg)

    print("Root length:", len(hbs.root))
    print("Verify correct message:", hbs.verify(msg, signed))
    print("Verify wrong message:", hbs.verify(b"wrong", signed))

    try:
        hbs.sign(0, msg)
        print("Reuse test failed")
    except ValueError as e:
        print("Reuse test passed:", e)

    print("Done.")
'''