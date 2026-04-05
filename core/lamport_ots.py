import secrets
from .hash_utils import H, digest_to_bits


class LamportOTS:
    # Lamport One-Time Signature scheme
    # initialize with number of bits and secret size in bytes
    def __init__(self, n_bits=256, secret_bytes=32):
        self.n_bits = n_bits
        self.secret_bytes = secret_bytes

    # Generate a key pair (private and public keys)
    def keygen(self):
        zero_secrets = [secrets.token_bytes(self.secret_bytes) for _ in range(self.n_bits)]
        one_secrets = [secrets.token_bytes(self.secret_bytes) for _ in range(self.n_bits)]

        zero_hashes = [H(x) for x in zero_secrets]
        one_hashes = [H(x) for x in one_secrets]

        private_key = {
            "zero": zero_secrets,
            "one": one_secrets,
        }

        public_key = {
            "zero": zero_hashes,
            "one": one_hashes,
        }

        return private_key, public_key
    

    # Sign a message using the private key
    def sign(self, message: bytes, private_key):
        bits = digest_to_bits(message)
        signature = []

        for i, bit in enumerate(bits):
            if bit == 0:
                signature.append(private_key["zero"][i])
            else:
                signature.append(private_key["one"][i])

        return signature

    # Verify a signature using the public key
    def verify(self, message: bytes, signature, public_key):
        bits = digest_to_bits(message)

        if len(signature) != self.n_bits:
            return False

        for i, bit in enumerate(bits):
            if bit == 0:
                if H(signature[i]) != public_key["zero"][i]:
                    return False
            else:
                if H(signature[i]) != public_key["one"][i]:
                    return False

        return True

# Test the Lamport OTS implementation
'''
if __name__ == "__main__":
    print("Testing lamport_ots.py...")

    ots = LamportOTS()
    sk, pk = ots.keygen()

    msg = b"hello"
    sig = ots.sign(msg, sk)

    print("Signature length:", len(sig))
    print("Verify correct message:", ots.verify(msg, sig, pk))
    print("Verify wrong message:", ots.verify(b"world", sig, pk))

    print("Done.")
'''