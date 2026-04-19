from core.merkle import MerkleTree
from core.hash_utils import hash_sha256

'''
message: (save: message_index, message_path, batch_root)
    build message merkle tree
    get_batch root
    sign(batch_root, keyid, parties)
    signed_data_on_batch_root
verify: 
    message + message_path -> verify message belong to batch_root
    batch_root + signed_data -> verify threshold signature

'''
class BatchThresholdHBS:
    def __init__(self, signer, verifier):
        self.signer = signer
        self.verifier = verifier

    def batch_sign(self, messages, keyid, parties):
        # error check
        if not isinstance(messages, list):
            raise TypeError("messages must be list")
        if len(messages) == 0:
            raise ValueError("cannot be an empty message")
        if not all(isinstance(message, bytes) for message in messages):
            raise TypeError("all messages must be bytes")
        
        # build merkle tree and set root
        message_tree = MerkleTree(messages)
        batch_root = message_tree.root
        # sign batch root
        threshold_signed_data = self.signer.sign(batch_root, keyid, parties)

        # message path
        message_paths = [message_tree.get_auth_path(index) for index in range(len(messages))]

        return {
            "batch_root": batch_root,
            "threshold_signed_data": threshold_signed_data,
            "message_paths": message_paths,
            "message_count": len(messages),
        }


    def batch_verify(self, message, message_index, batch_pack):
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if not isinstance(message_index, int):
            return False
        if not isinstance(batch_pack, dict):
            return False
        
        required = {
            "batch_root",
            "threshold_signed_data",
            "message_paths",
            "message_count",
        }
        if not all(key in batch_pack for key in required):
            return False
        batch_root = batch_pack["batch_root"]
        threshold_signed_data = batch_pack["threshold_signed_data"]
        message_paths = batch_pack["message_paths"]
        message_count = batch_pack["message_count"]

        if message_index <0 or message_index >= message_count:
            return False
        if not isinstance(message_paths, list) or not message_index < len(message_paths):
            return False
        
        # message path
        message_path = message_paths[message_index]
        if not self.verify_message_path(message, message_index, message_path, batch_root):
            return False

        return self.verifier.verify(batch_root, threshold_signed_data)
    
    def verify_message_path(self, message, index, path, root):
        if not isinstance(message, bytes):
            return False
        if not isinstance(index, int):
            return False
        if not isinstance(path, list):
            return False
        if not isinstance(root, bytes):
            return False
        if not all(isinstance(p, bytes) for p in path):
            return False
        # cureent and index for path verification
        current = hash_sha256(message)
        c_index = index
        for sibling in path:
            if c_index % 2 == 0:
                current = hash_sha256(current + sibling)
            else:
                current = hash_sha256(sibling + current)
            c_index //= 2
        return current == root