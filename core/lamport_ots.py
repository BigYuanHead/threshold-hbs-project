import secrets
from .hash_utils import hash_sha256, bits_converter


class LamportOTS:
    # Lamport One-Time Signature scheme
    # initialize with number of bits and secret size in bytes
    def __init__(self, n_bits=256, secret_bytes=32):
        self.n_bits = n_bits
        self.secret_bytes = secret_bytes
    
    # check key sturecture
    def check_key_structure(self, key, key_name):
        # dict type check
        if not isinstance(key, dict):
            raise TypeError(f"{key_name} must be a dict")
        # check zero and one in key
        if "zero" not in key or "one" not in key:
            raise ValueError(f"{key_name} must contain zero and one")
        # check zero and one are lists
        if not isinstance(key["zero"], list) or not isinstance(key["one"], list):
            raise TypeError(f"{key_name} zero and one must be lists")
        # check zero and one have correct length
        if len(key["zero"]) != self.n_bits or len(key["one"]) != self.n_bits:
            raise ValueError(f"{key_name} zero and one must have length {self.n_bits}")
        

    # Generate a key pair, private and public keys
    def keygen(self) -> tuple[dict, dict]:
        # secret generation
        zero_secrets = [secrets.token_bytes(self.secret_bytes) for _ in range(self.n_bits)]
        one_secrets = [secrets.token_bytes(self.secret_bytes) for _ in range(self.n_bits)]
        # public key generation
        zero_hashes = [hash_sha256(x) for x in zero_secrets]
        one_hashes = [hash_sha256(x) for x in one_secrets]

        # key structure in dic
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
    def sign(self, message: bytes, private_key) -> list[bytes]:
        # error check
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        # check key structure
        self.check_key_structure(private_key, "private_key")
        #convert message to bits
        bits = bits_converter(message)
        if len(bits) != self.n_bits:
            raise ValueError("Message must be exactly n_bits long")
        signature = []

        for i, bit in enumerate(bits):
            if bit == 0:
                signature.append(private_key["zero"][i])
            else:
                signature.append(private_key["one"][i])

        return signature

    # Verify a signature using the public key
    def verify(self, message: bytes, signature, public_key) -> bool:
        # error check
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        # check key structure
        self.check_key_structure(public_key, "public_key")

        bits = bits_converter(message)
        if len(bits) != self.n_bits:
            return False
        
        if len(signature) != self.n_bits:
            return False

        if len(signature) != self.n_bits:
            return False

        for i, bit in enumerate(bits):
            if bit == 0:
                if hash_sha256(signature[i]) != public_key["zero"][i]:
                    return False
            else:
                if hash_sha256(signature[i]) != public_key["one"][i]:
                    return False

        return True

