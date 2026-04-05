import hashlib

# Hash function using SHA-256
def H(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

# XOR two byte strings
def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

# Convert a hash digest to a list of bits
def digest_to_bits(data: bytes) -> list[int]:
    digest = H(data)
    bits = "".join(f"{byte:08b}" for byte in digest)
    return [int(bit) for bit in bits]

# Test the functions
'''
if __name__ == "__main__":
    print("Testing hash_utils.py...")

    h = H(b"hello")
    print("H(b'hello') length:", len(h))
    print("H(b'hello'):", h.hex())

    x = xor_bytes(b"\x01\x02", b"\x03\x04")
    print("xor_bytes result:", x)

    bits = digest_to_bits(b"hello")
    print("digest_to_bits length:", len(bits))
    print("first 16 bits:", bits[:16])

    print("Done.")
'''