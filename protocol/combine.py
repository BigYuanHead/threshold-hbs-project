# Combination logic for XOR additive signature shares.

from .utils import xor_many


def combine_signature_shares(signature_shares: list[list[bytes]]) -> list[bytes]:
    if not isinstance(signature_shares, list):
        raise TypeError("signature_shares must be a list")
    if len(signature_shares) == 0:
        raise ValueError("signature_shares cannot be empty")
    if not all(isinstance(share, list) for share in signature_shares):
        raise TypeError("each signature share must be a list")

    signature_length = len(signature_shares[0])
    if signature_length == 0:
        raise ValueError("signature shares cannot be empty")

    for share in signature_shares:
        if len(share) != signature_length:
            raise ValueError("all signature shares must have the same length")
        if not all(isinstance(value, bytes) for value in share):
            raise TypeError("all signature share values must be bytes")

    combined_signature = []
    for index in range(signature_length):
        combined_signature.append(xor_many([share[index] for share in signature_shares]))

    return combined_signature
