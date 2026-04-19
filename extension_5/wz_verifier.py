from typing import Optional

from .winternitz_standardized import WinternitzStandardized
from core.hash_utils import hash_sha256
from protocol.utils import validate_positive_int


class WinternitzVerifier:
    def __init__(self, root: bytes, total_keys: Optional[int] = None, backend=None):
        if not isinstance(root, bytes):
            raise TypeError("root must be bytes")

        self.root = root
        self.total_keys = total_keys
        self.backend = backend or WinternitzStandardized(w=16)

    def verify_public_key_path(self, public_key, keyid, path):
        if not isinstance(keyid, int):
            return False
        if keyid < 0:
            return False
        if not isinstance(path, list) or not all(isinstance(value, bytes) for value in path):
            return False
        try:
            current = hash_sha256(self.backend.serialize_public_key(public_key))
        except (TypeError, ValueError):
            return False
        c_index = keyid
        for sibling in path:
            if c_index % 2 == 0:
                current = hash_sha256(current + sibling)
            else:
                current = hash_sha256(sibling + current)
            c_index //= 2
        return current == self.root
        
    def verify(self, message, signed_data):
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if not isinstance(signed_data, dict):
            return False
        required_fields = ("keyid", "public_key", "signature", "path")
        if not all(field in signed_data for field in required_fields):
            return False
        k_id = signed_data["keyid"]
        if not isinstance(k_id, int) or k_id < 0:
            return False
        if self.total_keys is not None:
            validate_positive_int(self.total_keys, "total_keys")
            if k_id >= self.total_keys:
                return False
        public_key = signed_data["public_key"]
        signature = signed_data["signature"]
        path = signed_data["path"]

        try:
            if not self.backend.verify(message, signature, public_key):
                return False
        except (TypeError, ValueError, IndexError):
            return False
        return self.verify_public_key_path(public_key, k_id, path)