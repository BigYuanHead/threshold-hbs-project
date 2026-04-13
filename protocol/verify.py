# Independent verification for threshold-produced Lamport HBS signatures.

from typing import Optional

from core.hash_utils import hash_sha256
from core.lamport_ots import LamportOTS
from .utils import serialize_public_key, validate_positive_int


def verify_public_key_path(public_key: dict, keyid: int, path: list[bytes], root: bytes) -> bool:
    if not isinstance(root, bytes):
        raise TypeError("root must be bytes")
    if not isinstance(keyid, int):
        return False
    if keyid < 0:
        return False
    if not isinstance(path, list) or not all(isinstance(value, bytes) for value in path):
        return False

    try:
        current = hash_sha256(serialize_public_key(public_key))
    except (TypeError, ValueError):
        return False

    current_index = keyid
    for sibling in path:
        if current_index % 2 == 0:
            current = hash_sha256(current + sibling)
        else:
            current = hash_sha256(sibling + current)
        current_index //= 2

    return current == root


def verify_threshold_signature(
    message: bytes,
    signed_data: dict,
    root: bytes,
    total_keys: Optional[int] = None,
) -> bool:
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")
    if not isinstance(root, bytes):
        raise TypeError("root must be bytes")
    if not isinstance(signed_data, dict):
        return False

    required_fields = ("keyid", "public_key", "signature", "path")
    if not all(field in signed_data for field in required_fields):
        return False

    keyid = signed_data["keyid"]
    if not isinstance(keyid, int):
        return False
    if keyid < 0:
        return False

    if total_keys is not None:
        validate_positive_int(total_keys, "total_keys")
        if keyid >= total_keys:
            return False

    public_key = signed_data["public_key"]
    signature = signed_data["signature"]
    path = signed_data["path"]

    try:
        if not LamportOTS().verify(message, signature, public_key):
            return False
    except (TypeError, ValueError, IndexError):
        return False

    return verify_public_key_path(public_key, keyid, path, root)
