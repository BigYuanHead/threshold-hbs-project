# Untrusted aggregator for threshold HBS signing.

from protocol.combine import combine_signature_shares


class UntrustedServer:
    def __init__(self, public_params: dict):
        if not isinstance(public_params, dict):
            raise TypeError("public_params must be a dict")

        required_fields = ("root", "total_keys", "n_parties", "public_keys", "auth_paths")
        if not all(field in public_params for field in required_fields):
            raise ValueError("public_params is missing required fields")

        self.public_params = public_params

    def sign(self, message: bytes, keyid: int, parties: list) -> dict:
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if not isinstance(keyid, int):
            raise TypeError("keyid must be an integer")
        if keyid < 0 or keyid >= self.public_params["total_keys"]:
            raise ValueError("keyid out of range")
        if not isinstance(parties, list):
            raise TypeError("parties must be a list")
        if len(parties) != self.public_params["n_parties"]:
            raise ValueError("this minimal protocol requires all n parties")

        responses = [party.sign_share(message, keyid) for party in parties]
        refused = [response for response in responses if not response.get("accepted", False)]
        if refused:
            reasons = ", ".join(
                f"party {response.get('party_id')}: {response.get('reason')}" for response in refused
            )
            raise ValueError(f"not enough signature shares: {reasons}")

        party_ids = [response["party_id"] for response in responses]
        if len(set(party_ids)) != len(party_ids):
            raise ValueError("duplicate party responses")

        signature_shares = [
            response["signature_share"]
            for response in sorted(responses, key=lambda response: response["party_id"])
        ]
        combined_signature = combine_signature_shares(signature_shares)

        return {
            "keyid": keyid,
            "public_key": self.public_params["public_keys"][keyid],
            "signature": combined_signature,
            "path": self.public_params["auth_paths"][keyid],
            "party_ids": sorted(party_ids),
        }
