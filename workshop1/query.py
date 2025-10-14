#Russell
from tree23 import TreeNode

def find_terms_by_prefix(root: 'TreeNode', pattern: str) -> tuple[list[str], int]:
    """
    Input: tree root, pattern string with optional '*'
    Output: (list of matching terms, number of nodes visited)

    - '*' at start or end can match any number of characters
    - '*' in the middle matches exactly one character
    """
    matches = []
    steps = 0

    def match_pattern(term: str, pattern: str) -> bool:
        if "*" not in pattern:
            return term == pattern

        if pattern.startswith("*") and pattern.endswith("*"):
            inner = pattern.strip("*")
            return inner in term

        elif pattern.startswith("*"):
            suffix = pattern[1:]
            return term.endswith(suffix)

        elif pattern.endswith("*"):
            prefix = pattern[:-1]
            return term.startswith(prefix)

        else:
            # '*' in the middle – match exactly one character
            parts = pattern.split("*")
            if len(parts) != 2:
                return False  # only support one '*' in middle for now

            start, end = parts
            if len(term) != len(start) + 1 + len(end):
                return False

            return term.startswith(start) and term.endswith(end)

    def traverse(node: 'TreeNode'):
        nonlocal steps
        if node is None:
            return

        steps += 1

        for key in node.keys:
            if match_pattern(key, pattern):
                matches.append(key)

        for child in node.children:
            traverse(child)

    traverse(root)
    return matches, steps
