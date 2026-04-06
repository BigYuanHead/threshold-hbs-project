from .hash_utils import hash_sha256

# Merkle Tree implementation
class MerkleTree:
    # Initialize the Merkle Tree with a list of leaves (data blocks)
    def __init__(self, leaves):
        if not isinstance(leaves, list):
            raise TypeError("leaves must be a list of bytes")
        if len(leaves) == 0:
            raise ValueError("leaves cannot be empty")
        if len(leaves) & (len(leaves) - 1) != 0:
            raise ValueError("Number of leaves must be a power of 2")
        if not all(isinstance(leaf, bytes) for leaf in leaves):
            raise TypeError("All leaves must be bytes")
        
        self.leaves = leaves
        self.levels = self.build_tree(leaves)
        self.root = self.levels[-1][0]

    # Build the Merkle Tree and return the levels
    def build_tree(self, leaves: list[bytes]) -> list[list[bytes]]:
        # hash(leaf) as level 0
        current_level = [hash_sha256(leaf) for leaf in leaves]
        levels = [current_level]

        # build left and right leaf and hash(l+r) as parent until we get the root
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1]
                parent = hash_sha256(left + right)
                next_level.append(parent)

            levels.append(next_level)
            current_level = next_level

        return levels

    # Get the authentication path for a given leaf index
    def get_auth_path(self, index: int) -> list[bytes]:
        # error check
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        
        if index < 0 or index >= len(self.leaves):
            raise ValueError("index out of range")
        path = []
        current_index = index

        for level in self.levels[:-1]:
            sibling_index = current_index ^ 1
            path.append(level[sibling_index])
            current_index //= 2

        return path

    # Verify the authentication path for a given leaf, index, path, and root
    def verify_path(self, leaf: bytes, index: int, path: list[bytes], root: bytes) -> bool:
        if not isinstance(leaf, bytes):
            return False
        if not isinstance(index, int):
            return False
        if index < 0:
            return False
        if not isinstance(path, list) or not all(isinstance(p, bytes) for p in path):
            return False
        if not isinstance(root, bytes):
            return False
        current = hash_sha256(leaf)
        current_index = index

        for sibling in path:
            if current_index % 2 == 0:
                current = hash_sha256(current + sibling)
            else:
                current = hash_sha256(sibling + current)

            current_index //= 2

        return current == root

