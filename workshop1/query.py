# Rusel
from 23tree import TreeNode
def find_terms_by_prefix(root: 'TreeNode', prefix: str) -> tuple[list[str], int]:
    """
    Input:  tree root, prefix string (e.g., 's')
    Output: (list of matching terms, number of nodes visited)
    Traverse tree to collect all terms beginning with prefix.
    """
