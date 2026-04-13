# Public verifier for threshold-produced HBS signatures.

from typing import Optional

from protocol.verify import verify_threshold_signature


class Verifier:
    def __init__(self, root: bytes, total_keys: Optional[int] = None):
        if not isinstance(root, bytes):
            raise TypeError("root must be bytes")
        self.root = root
        self.total_keys = total_keys

    def verify(self, message: bytes, signed_data: dict) -> bool:
        return verify_threshold_signature(
            message=message,
            signed_data=signed_data,
            root=self.root,
            total_keys=self.total_keys,
        )
