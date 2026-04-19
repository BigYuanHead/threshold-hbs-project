from typing import Optional

from protocol.signing import create_signature_share


class KOfNParty:
    def __init__(self, party_id, share_bundle, refused_messages: Optional[set[bytes]] = None):
        if not isinstance(party_id, int):
            raise TypeError("party_id must be an integer")
        if not isinstance(share_bundle, dict):
            raise TypeError("share_bundle must be a dict")
        required_fields = ("party_id", "subset_shares")
        if not all(field in share_bundle for field in required_fields):
            raise ValueError("share_bundle must contain party_id and subset_shares")
        if share_bundle["party_id"] != party_id:
            raise ValueError("party_id does not match share_bundle")
        if not isinstance(share_bundle["subset_shares"], dict):
            raise TypeError("subset_shares must be a dict")

        self.party_id = party_id
        self.subset_shares = share_bundle["subset_shares"]
        self.used_keys = set()
        self.refused_messages = refused_messages or set()

    def sign_share(self, message, keyid, subset_id):
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if not isinstance(keyid, int):
            raise TypeError("keyid must be an integer")
        if not isinstance(subset_id, int):
            raise TypeError("subset_id must be an integer")

        if subset_id not in self.subset_shares:
            return {
                "accepted": False,
                "party_id": self.party_id,
                "keyid": keyid,
                "subset_id": subset_id,
                "reason": "party not in selected subtree",
            }

        subset_share = self.subset_shares[subset_id]
        key_shares = subset_share["key_shares"]
        if keyid < 0 or keyid >= len(key_shares):
            raise ValueError("keyid out of range")

        if message in self.refused_messages:
            return {
                "accepted": False,
                "party_id": self.party_id,
                "keyid": keyid,
                "subset_id": subset_id,
                "reason": "message refused",
            }

        used_key = (subset_id, keyid)
        if used_key in self.used_keys:
            return {
                "accepted": False,
                "party_id": self.party_id,
                "keyid": keyid,
                "subset_id": subset_id,
                "reason": "keyid already used in selected subtree",
            }

        signature_share = create_signature_share(message, key_shares[keyid])
        self.used_keys.add(used_key)

        return {
            "accepted": True,
            "party_id": self.party_id,
            "keyid": keyid,
            "subset_id": subset_id,
            "signature_share": signature_share,
        }
