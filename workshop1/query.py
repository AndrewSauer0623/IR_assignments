#Russell
from tree23 import TreeNode

def rotate_pattern(pattern: str) -> str:
    """Rotate pattern so '*' ends up at the end for permuterm prefix search."""
    if '*' not in pattern:
        return pattern + '$'
    star_index = pattern.index('*')
    before_star = pattern[:star_index]
    after_star = pattern[star_index + 1:]
    return after_star + '$' + before_star + '*'


def match_pattern(term: str, pattern: str) -> bool:
    """Return True if term matches the permuterm prefix derived from the pattern."""
    rotated = rotate_pattern(pattern)
    prefix = rotated.replace('*', '')
    return term.startswith(prefix)


def find_terms_by_prefix(root: 'TreeNode', pattern: str) -> tuple[list[str], int]:
    """
    Input: tree root, pattern string with optional '*'
    Output: (list of matching terms, number of nodes visited)
    """
    matches = []
    steps = 0

    def traverse(node: 'TreeNode'):
        nonlocal steps
        if node is None:
            return
        steps += 1

        for key in node.keys:
            if match_pattern(key, pattern):
                # rotate back to get original term
                if '$' in key:
                    dollar_index = key.index('$')
                    orig = key[dollar_index + 1:] + key[:dollar_index]
                else:
                    orig = key
                if orig not in matches:
                    matches.append(orig)

        for child in node.children:
            traverse(child)

    traverse(root)
    return matches, steps

def compute_query_weights(query_terms, inverted_index):
    """
    Input:  list of terms, inverted_index
    Output: {term: query_weight}

    Steps:
      - compute tf and log(tf)
      - compute IDF = log(N / df)
      - multiply log(tf)*idf
      - normalize to unit length
    """
    pass


def rank_documents(query_weights, inverted_index):
    """
    Input:  query_weights, inverted_index
    Output: ranked list of (doc_id, score)

    Steps:
      - for each query term, get postings
      - multiply doc term weight × query term weight
      - sum for each doc
      - sort by score descending
    """
    pass
