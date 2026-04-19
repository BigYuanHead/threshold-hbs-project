from typing import Optional

from core.hash_utils import hash_sha256
from core.lamport_ots import LamportOTS
from protocol.utils import validate_positive_int
from protocol.verify import verify_public_key_path


def verify_subtree_path(subtree_root, subtree_id, subtree_path, root):
    if not isinstance(subtree_root, bytes):
        return False
    if not isinstance(subtree_id, int) or subtree_id < 0:
        return False
    if not isinstance(subtree_path, list):
        return False
    if not all(isinstance(value, bytes) for value in subtree_path):
        return False
    if not isinstance(root, bytes):
        return False

    current = hash_sha256(subtree_root)
    current_index = subtree_id
    for sibling in subtree_path:
        if current_index % 2 == 0:
            current = hash_sha256(current + sibling)
        else:
            current = hash_sha256(sibling + current)
        current_index //= 2

    return current == root


def verify_kofn_signature(message, signed_data, root, total_keys: Optional[int] = None):
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")
    if not isinstance(root, bytes):
        raise TypeError("root must be bytes")
    if not isinstance(signed_data, dict):
        return False

    required_fields = (
        "keyid",
        "public_key",
        "signature",
        "path",
        "subtree_id",
        "subtree_root",
        "subtree_path",
    )
    if not all(field in signed_data for field in required_fields):
        return False

    keyid = signed_data["keyid"]
    if not isinstance(keyid, int) or keyid < 0:
        return False
    if total_keys is not None:
        validate_positive_int(total_keys, "total_keys")
        if keyid >= total_keys:
            return False

    public_key = signed_data["public_key"]
    signature = signed_data["signature"]
    path = signed_data["path"]
    subtree_root = signed_data["subtree_root"]
    subtree_id = signed_data["subtree_id"]
    subtree_path = signed_data["subtree_path"]

    try:
        if not LamportOTS().verify(message, signature, public_key):
            return False
    except (TypeError, ValueError, IndexError):
        return False

    if not verify_public_key_path(public_key, keyid, path, subtree_root):
        return False

    return verify_subtree_path(subtree_root, subtree_id, subtree_path, root)


class KOfNVerifier:
    def __init__(self, root: Optional[bytes] = None, total_keys: Optional[int] = None):
        if root is not None and not isinstance(root, bytes):
            raise TypeError("root must be bytes")
        self.root = root
        self.total_keys = total_keys

    def verify(self, message, signed_data, root: Optional[bytes] = None):
        verify_root = root or self.root
        if verify_root is None:
            raise ValueError("root is required")
        return verify_kofn_signature(
            message=message,
            signed_data=signed_data,
            root=verify_root,
            total_keys=self.total_keys,
        )
