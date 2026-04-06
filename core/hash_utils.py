import hashlib

# Hash function using SHA-256
def hash_sha256(data: bytes) -> bytes:
    # error check
    if not isinstance(data, bytes):
        raise TypeError("Input must be bytes")
    h = hashlib.sha256(data).digest()
    return h

# XOR two byte strings
def xor_calculator(a: bytes, b: bytes) -> bytes:
    # error check
    if not isinstance(a, bytes) or not isinstance(b, bytes):
        raise TypeError("Input must be bytes")
    if len(a) != len(b):
        raise ValueError("Input must be same length")
    xor = bytes(x ^ y for x, y in zip(a, b))
    return xor

# Convert a hash digest to a list of bits
def bits_converter(data: bytes) -> list[int]:
    # error check
    if not isinstance(data, bytes):
        raise TypeError("Input must be bytes")
    digest = hash_sha256(data)
    bits = "".join(f"{byte:08b}" for byte in digest)
    list_bits = [int(bit) for bit in bits]
    return list_bits

