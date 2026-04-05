from .hash_utils import H

# Merkle Tree implementation
class MerkleTree:
    # Initialize the Merkle Tree with a list of leaves (data blocks)
    def __init__(self, leaves):
        self.leaves = leaves
        self.levels = self.build_tree(leaves)
        self.root = self.levels[-1][0]

    # Build the Merkle Tree and return the levels
    def build_tree(self, leaves):
        current_level = [H(leaf) for leaf in leaves]
        levels = [current_level]

        while len(current_level) > 1:
            next_level = []

            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1]
                parent = H(left + right)
                next_level.append(parent)

            levels.append(next_level)
            current_level = next_level

        return levels

    # Get the authentication path for a given leaf index
    def get_auth_path(self, index):
        path = []
        current_index = index

        for level in self.levels[:-1]:
            sibling_index = current_index ^ 1
            path.append(level[sibling_index])
            current_index //= 2

        return path

    # Verify the authentication path for a given leaf, index, path, and root
    @staticmethod
    def verify_path(leaf, index, path, root):
        current = H(leaf)
        current_index = index

        for sibling in path:
            if current_index % 2 == 0:
                current = H(current + sibling)
            else:
                current = H(sibling + current)

            current_index //= 2

        return current == root

# test the Merkle Tree implementation
'''
if __name__ == "__main__":
    print("Testing merkle.py...")

    leaves = [b"a", b"b", b"c", b"d"]
    tree = MerkleTree(leaves)

    print("Root length:", len(tree.root))
    print("Root:", tree.root.hex())

    index = 2
    path = tree.get_auth_path(index)

    print("Path length:", len(path))
    print("Verify correct leaf:", MerkleTree.verify_path(leaves[index], index, path, tree.root))
    print("Verify wrong leaf:", MerkleTree.verify_path(b"x", index, path, tree.root))

    print("Done.")
'''