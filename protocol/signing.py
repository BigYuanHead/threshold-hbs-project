# Signature-share generation for threshold Lamport signing.

from core.hash_utils import bits_converter
from .utils import validate_lamport_key


def create_signature_share(message: bytes, key_share: dict) -> list[bytes]:
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")

    n_bits = validate_lamport_key(key_share, "key_share")
    bits = bits_converter(message)
    if len(bits) != n_bits:
        raise ValueError("message digest length does not match key share length")

    signature_share = []
    for index, bit in enumerate(bits):
        if bit == 0:
            signature_share.append(key_share["zero"][index])
        else:
            signature_share.append(key_share["one"][index])

    return signature_share
