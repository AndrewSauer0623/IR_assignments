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

    import re

def match_pattern(term: str, pattern: str) -> bool:
    regex_pattern = re.escape(pattern).replace(r'\*', '.')
    if pattern.startswith('*') and pattern.endswith('*') and len(pattern) > 2:
        inner = re.escape(pattern.strip('*'))
        regex_pattern = f".*{inner}.*"
    elif pattern.startswith('*'):
        suffix = re.escape(pattern[1:])
        regex_pattern = f".*{suffix}$"
    elif pattern.endswith('*'):
        prefix = re.escape(pattern[:-1])
        regex_pattern = f"^{prefix}.*"
    else:
        regex_pattern = f"^{regex_pattern}$"

    return re.match(regex_pattern, term) is not None


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
