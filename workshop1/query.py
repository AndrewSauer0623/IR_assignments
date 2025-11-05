
import math
from tree23 import TreeNode
from preprocess import preprocess_text
from index_builder import build_inverted_index, normalize_document_weights
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
    Compute query weights using ltc scheme:
    l = log(tf)
    t = idf = log(N/df)
    c = cosine normalization
    """
    tf_counts = {}
    for term in query_terms:
        tf_counts[term] = tf_counts.get(term, 0) + 1
    N = len({doc for term in inverted_index for doc in inverted_index[term]['postings']}) or 1
    weights = {}
    for term, tf in tf_counts.items():
        df = inverted_index.get(term, {}).get('df', 1)
        log_tf = 1 + math.log(tf)
        idf = math.log(N / df)
        weights[term] = log_tf * idf
    norm = math.sqrt(sum(w ** 2 for w in weights.values()))
    if norm > 0:
        for term in weights:
            weights[term] /= norm

    return weights
def rank_documents(query_weights, inverted_index):
    """
    Input: query_weights (ltc), inverted_index (lnc)
    Output: ranked list of (doc_id, score)
    """
    doc_weights = {}

    for term, q_weight in query_weights.items():
        if term not in inverted_index:
            continue

        postings = inverted_index[term]['postings']
        for doc_id, stats in postings.items():
            d_weight = stats.get('normalized', 0.0)
            doc_weights[doc_id] = doc_weights.get(doc_id, 0.0) + q_weight * d_weight

    ranked = sorted(doc_weights.items(), key=lambda x: x[1], reverse=True)
    return ranked
def main():
    documents = {
        1: "for english model retireval have a relevance model while vector space model retrieval",
        2: "r-precision measure is relevant to average precision measure",
        3: "most efficient retrieval models are language model and vector space model",
        4: "english is the most efficient language",
        5: "retrieval efficiency is measured by average precision",
    }
    doc_tokens = {doc_id: preprocess_text(text) for doc_id, text in documents.items()}
    from bailey import compute_term_frequencies
    term_freqs = compute_term_frequencies(doc_tokens)
    inverted_index = build_inverted_index(term_freqs)
    inverted_index = normalize_document_weights(inverted_index)
    terms = list(inverted_index.keys())
    perm_root = build_permuterm_index_from_terms(terms)
    query = "effici* retrieval model"
    query_tokens = preprocess_text(query)

    expanded_terms = []
    for qt in query_tokens:
        if '*' in qt:
            matches, _ = find_terms_by_prefix(perm_root, qt)
            expanded_terms.extend(matches)
        else:
            expanded_terms.append(qt)
    q_weights = compute_query_weights(expanded_terms, inverted_index)
    ranked_results = rank_documents(q_weights, inverted_index)
    print_trec_format(ranked_results, query_id="001", run_name="lnc.ltc_demo")


if __name__ == "__main__":
    main()
