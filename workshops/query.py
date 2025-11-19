# Russell
import math
from typing import List, Tuple
from tree23 import TreeNode

def rotate_pattern(pattern: str) -> str:
    """Rotate pattern so '*' is at the end for prefix search."""
    if '*' not in pattern:
        return pattern + '$'
    star_index = pattern.index('*')
    before_star: str = pattern[:star_index]
    after_star: str = pattern[star_index + 1:]
    return after_star + '$' + before_star  # remove '*' in rotation

def match_pattern(term: str, rotated_prefix: str) -> bool:
    """Check if a permuterm key matches the rotated prefix."""
    return term.startswith(rotated_prefix)

def find_terms_by_prefix(root: TreeNode, pattern: str) -> Tuple[List[str], int]:
    """
    Search permuterm tree for terms matching a wildcard pattern.
    Returns (list of original terms, number of nodes visited).
    """
    matches: List[str] = []
    steps: int = 0
    rotated_prefix: str = rotate_pattern(pattern)

    def traverse(node: TreeNode) -> None:
        nonlocal steps
        if node is None:
            return
        steps += 1
        for key in node.keys:
            if match_pattern(key, rotated_prefix):
                # original term stored as value in term_documents
                for original_term in node.term_documents[key]:
                    if original_term not in matches:
                        matches.append(original_term)
        for child in node.children:
            traverse(child)

    traverse(root)
    return matches, steps

def compute_query_weights(query_terms: List[str], inverted_index: dict) -> dict[str, float]:
    """
    Compute query weights using ltc scheme:
    l = log(tf)
    t = idf = log(N/df)
    c = cosine normalization
    """
    tf_counts: dict[str, int] = {}
    for term in query_terms:
        tf_counts[term] = tf_counts.get(term, 0) + 1

    N: int = len({doc for term in inverted_index for doc in inverted_index[term]['postings']}) or 1
    weights: dict[str, float] = {}
    for term, tf in tf_counts.items():
        df: int = inverted_index.get(term, {}).get('df', 1)
        log_tf: float = 1 + math.log(tf)
        idf: float = math.log(N / df)
        weights[term] = log_tf * idf

    norm: float = math.sqrt(sum(w ** 2 for w in weights.values()))
    if norm > 0:
        for term in weights:
            weights[term] /= norm

    return weights

def rank_documents(query_weights: dict[str, float], inverted_index: dict) -> List[Tuple[int, float]]:
    """
    Compute cosine similarity of query against all documents.
    Returns a ranked list of (doc_id, score)
    """
    doc_weights: dict[int, float] = {}
    for term, q_weight in query_weights.items():
        if term not in inverted_index:
            continue
        postings: dict[int, dict] = inverted_index[term]['postings']
        for doc_id, stats in postings.items():
            d_weight: float = stats.get('normalized', 0.0)
            doc_weights[doc_id] = doc_weights.get(doc_id, 0.0) + q_weight * d_weight

    ranked: List[Tuple[int, float]] = sorted(doc_weights.items(), key=lambda x: x[1], reverse=True)
    return ranked
