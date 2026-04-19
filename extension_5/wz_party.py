from extension_5.winternitz_standardized import WinternitzStandardized

class WinternitzParty:
    def __init__(self, party_id, share_bundle, backend=None, refused_messages=None):
        if not isinstance(party_id, int):
            raise TypeError("party_id must be an integer")
        if not isinstance(share_bundle, dict):
            raise TypeError("share_bundle must be a dict")
        if "party_id" not in share_bundle or "key_shares" not in share_bundle:
            raise ValueError("share_bundle must contain party_id and key_shares")
        if share_bundle["party_id"] != party_id:
            raise ValueError("party_id does not match share_bundle")
        if not isinstance(share_bundle["key_shares"], list):
            raise TypeError("key_shares must be a list")

        self.party_id = party_id
        self.key_shares = share_bundle["key_shares"]
        self.backend = WinternitzStandardized(w=16)
        self.used_keyids = set()
        self.refused_messages = refused_messages or set()

    def sign_share(self, message, keyid):
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if not isinstance(keyid, int):
            raise TypeError("keyid must be an integer")
        if keyid < 0 or keyid >= len(self.key_shares):
            raise ValueError("keyid out of range")

        if message in self.refused_messages:
            return {
                "accepted": False,
                "party_id": self.party_id,
                "keyid": keyid,
                "reason": "message refused",
            }

        if keyid in self.used_keyids:
            return {
                "accepted": False,
                "party_id": self.party_id,
                "keyid": keyid,
                "reason": "keyid already used",
            }
        key_share = self.key_shares[keyid]
        signature_share = self.backend.create_signature_shares(message, key_share)
        self.used_keyids.add(keyid)

        return {
            "accepted": True,
            "party_id": self.party_id,
            "keyid": keyid,
            "signature_share": signature_share,
        }