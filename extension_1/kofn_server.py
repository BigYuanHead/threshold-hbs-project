from protocol.combine import combine_signature_shares


class KOfNUntrustedServer:
    def __init__(self, public_params):
        if not isinstance(public_params, dict):
            raise TypeError("public_params must be a dict")

        required_fields = ("root", "total_keys", "n_parties", "threshold_k", "subtrees")
        if not all(field in public_params for field in required_fields):
            raise ValueError("public_params is missing required fields")

        self.public_params = public_params
        self.subtrees_by_parties = {}
        for subtree in public_params["subtrees"]:
            party_ids = tuple(sorted(subtree["party_ids"]))
            self.subtrees_by_parties[party_ids] = subtree

    def sign(self, message, keyid, parties):
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if not isinstance(keyid, int):
            raise TypeError("keyid must be an integer")
        if keyid < 0 or keyid >= self.public_params["total_keys"]:
            raise ValueError("keyid out of range")
        if not isinstance(parties, list):
            raise TypeError("parties must be a list")

        threshold_k = self.public_params["threshold_k"]
        if len(parties) != threshold_k:
            raise ValueError("this k-of-n protocol requires exactly k selected parties")

        party_ids = [party.party_id for party in parties]
        if len(set(party_ids)) != len(party_ids):
            raise ValueError("duplicate parties")

        selected_party_ids = tuple(sorted(party_ids))
        if selected_party_ids not in self.subtrees_by_parties:
            raise ValueError("no k-of-k subtree for selected parties")

        subtree = self.subtrees_by_parties[selected_party_ids]
        subset_id = subtree["subset_id"]

        responses = [party.sign_share(message, keyid, subset_id) for party in parties]
        refused = [response for response in responses if not response.get("accepted", False)]
        if refused:
            reasons = ", ".join(
                f"party {response.get('party_id')}: {response.get('reason')}"
                for response in refused
            )
            raise ValueError(f"not enough signature shares: {reasons}")

        response_party_ids = [response["party_id"] for response in responses]
        if sorted(response_party_ids) != list(selected_party_ids):
            raise ValueError("party responses do not match selected subtree")
        if any(response["keyid"] != keyid for response in responses):
            raise ValueError("party responses do not match requested keyid")
        if any(response["subset_id"] != subset_id for response in responses):
            raise ValueError("party responses do not match selected subtree")

        signature_shares = [
            response["signature_share"]
            for response in sorted(responses, key=lambda response: response["party_id"])
        ]
        combined_signature = combine_signature_shares(signature_shares)

        return {
            "keyid": keyid,
            "public_key": subtree["public_keys"][keyid],
            "signature": combined_signature,
            "path": subtree["auth_paths"][keyid],
            "party_ids": list(selected_party_ids),
            "threshold_k": threshold_k,
            "subtree_id": subset_id,
            "subtree_root": subtree["root"],
            "subtree_path": subtree["subtree_path"],
        }
