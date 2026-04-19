from core.hash_utils import hash_sha256
import secrets, math

class WinternitzOTS:
    def __init__(self, w=16, digest_size=32, secret_size=32):
        # error check
        if not isinstance(w, int) or w <= 1:
            raise ValueError("w must be an integer and greater than 1")
        if w & (w - 1) != 0:
            raise ValueError("w must be a power of 2")
        # iniialization
        self.w = w
        self.max_digit = w - 1
        self.digest_size = digest_size
        self.secret_size = secret_size
        self.bits_per_digit = int(math.log2(w))
        self.message_digits_count = (digest_size *8) // self.bits_per_digit
        max_checksum = self.message_digits_count * self.max_digit
        self.checksum_digits_count = self._digit_count(max_checksum)
        self.total_chains = self.message_digits_count + self.checksum_digits_count

    # calculation of digit count for checksum
    def _digit_count(self, value):
        ct = 1
        while value >= self.w:
            value //= self.w
            ct += 1
        return ct
    
    def _hash_chain(self, value, steps):
        # error check
        if not isinstance(value, bytes):
            raise TypeError("value must be bytes")
        if not isinstance(steps, int) or steps < 0:
            raise ValueError("steps must be a non-negative integer")
        current = value
        for _ in range(steps):
            current = hash_sha256(current)
        return current
    
    # convert message to base w digits
    def _to_base_w(self, data, digit_count):
        # error check
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        
        value = int.from_bytes(data, "big")
        digits = []
        for _ in range(digit_count):
            digits.append(value % self.w)
            value //= self.w
        digits.reverse()
        return digits
    
    # calculate checksum
    def _message_to_digits(self, message):
        # error checkss
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        digest = hash_sha256(message)
        message_digits = self._to_base_w(digest, self.message_digits_count)

        checksum = sum(self.max_digit - d for d in message_digits)
        checksum_bytes = checksum.to_bytes((checksum.bit_length() + 7) // 8, "big")
        checksum_digits = self._to_base_w(checksum_bytes, self.checksum_digits_count)
        return message_digits + checksum_digits
    
    # key generation
    def keygen(self):
        private_chains = [secrets.token_bytes(self.secret_size) for _ in range(self.total_chains)]
        public_chains = [self._hash_chain(chain, self.max_digit) for chain in private_chains]
        private_key = {"w": self.w, "chains": private_chains}
        public_key = {"w": self.w, "chains": public_chains}
        return private_key, public_key
    
    # signature generation  
    # check key structure
    def _check_key(self, key, key_name):
        if not isinstance(key, dict):
            raise TypeError(f"{key_name} must be a dict")
        if "w" not in key or "chains" not in key:
            raise ValueError(f"{key_name} must contain w and chains")
        if key["w"] != self.w:
            raise ValueError(f"{key_name} w value must match WinternitzOTS w")
        if not isinstance(key["chains"], list) or len(key["chains"]) != self.total_chains:
            raise ValueError(f"{key_name} chains must be a list of length {self.total_chains}")
        if not all(isinstance(chain, bytes) for chain in key["chains"]):
            raise TypeError(f"{key_name} chains must be a list of bytes")



    def sign(self, message, private_key):
        # error check
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        self._check_key(private_key, "private_key")
        digits = self._message_to_digits(message)
        signature = []
        for i, digit in enumerate(digits):
            secret = private_key["chains"][i]
            signature.append(self._hash_chain(secret, digit))
        return signature
    
    # verify
    def verify(self, message, signature, public_key):
        # error check
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        self._check_key(public_key, "public_key")

        if not isinstance(signature, list) or len(signature) != self.total_chains:
            return False
        if not all(isinstance(s, bytes) for s in signature):
            return False
        digits = self._message_to_digits(message)
        for i, digit in enumerate(digits):
            remaining_steps = self.max_digit - digit
            expected = self._hash_chain(signature[i], remaining_steps)
            if expected != public_key["chains"][i]:
                return False
        return True
    
    def serialize_public_key(self, public_key):
        self._check_key(public_key, "public_key")
        return b"".join(public_key["chains"])
