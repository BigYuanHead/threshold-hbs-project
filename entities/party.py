# Party role for threshold Lamport signing.

from typing import Optional

from protocol.signing import create_signature_share


class Party:
    def __init__(self, party_id: int, share_bundle: dict, refused_messages: Optional[set[bytes]] = None):
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
        self.used_keyids = set()
        self.refused_messages = refused_messages or set()

    def sign_share(self, message: bytes, keyid: int) -> dict:
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

        signature_share = create_signature_share(message, self.key_shares[keyid])
        self.used_keyids.add(keyid)

        return {
            "accepted": True,
            "party_id": self.party_id,
            "keyid": keyid,
            "signature_share": signature_share,
        }
