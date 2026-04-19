from extension_5.winternitz_ots import WinternitzOTS
from protocol.utils import xor_many, validate_positive_int
import secrets

class WinternitzStandardized:
    def __init__(self, w=16):
        self.ots = WinternitzOTS(w=w)
        self.w = self.ots.w
        self.max_digit = self.ots.max_digit
        self.total_chains = self.ots.total_chains

    # use same things of WinternitzOTS
    def keygen(self):
        return self.ots.keygen()

    def sign(self, message, sk):
        return self.ots.sign(message, sk)

    def verify(self, message, sig, pk):
        return self.ots.verify(message, sig, pk)

    def serialize_public_key(self, sig):
        return self.ots.serialize_public_key(sig)
    ## new
    # xor split
    def xor_split_secrets(self, secret, n_parties):
        if not isinstance(secret, bytes):
            raise TypeError("secret must be bytes")
        validate_positive_int(n_parties, "n_parties")
        if n_parties == 1:
            return [secret]
        shares = [secrets.token_bytes(len(secret)) for _ in range(n_parties - 1)]
        final_share = xor_many([secret] + shares)
        shares.append(final_share)
        return shares
    
    # share private key
    def share_private_key(self, private_key, n_parties):
        self.ots._check_key(private_key, "private_key")
        validate_positive_int(n_parties, "n_parties")
        pty_shares = [{"w": self.w, "max_digit": self.max_digit, "total_chains": self.total_chains, "states_shares": []} for _ in range(n_parties)]
        for c_secret in private_key["chains"]:
            c_states = [self.ots._hash_chain(c_secret, i) for i in range(self.max_digit + 1)]
            split_states = [self.xor_split_secrets(state, n_parties) for state in c_states]
            for i in range(n_parties):
                party_chain_shares = [split_states[j][i] for j in range(self.max_digit + 1)]
                pty_shares[i]["states_shares"].append(party_chain_shares)
        return pty_shares
    
    def check_share_structure(self, pty_shares):
        if not isinstance(pty_shares, dict):
            raise ValueError(f"pty_shares must be a dict")
        required_keys = {"w", "max_digit", "total_chains", "states_shares"}
        if not all(key in pty_shares for key in required_keys):
            raise TypeError("Missing required keys in pty_shares")
        if pty_shares["w"] != self.w or pty_shares["max_digit"] != self.max_digit or pty_shares["total_chains"] != self.total_chains:
            raise ValueError("pty_shares w, max_digit, total_chains must match WinternitzOTS parameters")
        states_shares = pty_shares["states_shares"]
        if not isinstance(states_shares, list) or len(states_shares) != self.total_chains:
            raise ValueError(f"list: shares has wrong number of chains")
        for chain_shares in states_shares:
            if not isinstance(chain_shares, list) or len(chain_shares) != self.max_digit + 1:
                raise ValueError(f"list: shares has wrong number of states in a chain")
            for state_share in chain_shares:
                if not isinstance(state_share, bytes):
                    raise TypeError("all chains must be bytes")

    
    def create_signature_shares(self, message, pty_shares):
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        self.check_share_structure(pty_shares)
        digits = self.ots._message_to_digits(message)
        sig = []
        for i, digit in enumerate(digits):
            sig.append(pty_shares["states_shares"][i][digit])
        return sig
    
    def combine_sig_shares(self, sig_shares):
        if not isinstance(sig_shares, list) or len(sig_shares) == 0:
            raise ValueError(f"sig_shares cannot be an empty list")
        
        for share in sig_shares:
            if not isinstance(share, list):
                raise TypeError("All shares in sig_shares must be bytes")
            

        lens = len(sig_shares[0])
        if lens != self.total_chains:
            raise ValueError(f"it must be same length")
        for share in sig_shares:
            if len(share) != lens:
                raise ValueError(f"All shares in sig_shares must have the same length")
            if not all(isinstance(s, bytes) for s in share):
                raise TypeError("All shares in sig_shares must be bytes")
        combined_sig = []
        for i in range(lens):
            combined_sig.append(xor_many([share[i] for share in sig_shares]))
        return combined_sig
