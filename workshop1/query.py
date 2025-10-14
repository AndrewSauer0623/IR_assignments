#Russell
from tree23 import TreeNode

def find_terms_by_prefix(root: 'TreeNode', prefix: str) -> tuple[list[str], int]:
    """
    Input:  tree root, prefix string (e.g., 's', '*ing')
    Output: (list of matching terms, number of nodes visited)

    If prefix starts with '*', match terms that END with the given string.
    Else, match terms that START with the given string.
    """

    matches = []       # list of terms that match the prefix
    steps = 0          # how many nodes we visit in total

    # Determine if wildcard match (endswith) or normal prefix match (startswith)
    is_wildcard = prefix.startswith("*")
    actual_prefix = prefix[1:] if is_wildcard else prefix

    def traverse(node: 'TreeNode'):
        nonlocal steps
        if node is None:
            return

        steps += 1

        for key in node.keys:
            if is_wildcard:
                if key.endswith(actual_prefix):
                    matches.append(key)
            else:
                if key.startswith(actual_prefix):
                    matches.append(key)

        for child in node.children:
            traverse(child)

    traverse(root)
    return matches, steps
