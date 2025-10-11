# Russel
from tree23 import TreeNode

def find_terms_by_prefix(root: 'TreeNode', prefix: str) -> tuple[list[str], int]:
    """
    Input:  tree root, prefix string (e.g., 's')
    Output: (list of matching terms, number of nodes visited)
    Traverse tree to collect all terms beginning with prefix.
    """

    matches = []       # list of terms that match the prefix
    steps = 0          # how many nodes we visit in total

    # use a simple helper function to walk the tree
    def traverse(node: 'TreeNode'):
        nonlocal steps
        if node is None:
            return

        # count each node visited
        steps = steps + 1

        # check each key (term) stored in this node
        for key in node.keys:
            if key.startswith(prefix):
                matches.append(key)

        # visit each child node if they exist
        for child in node.children:
            traverse(child)

    # start traversal from the root
    traverse(root)

    # return both the matches and number of nodes visited
    return matches, steps

