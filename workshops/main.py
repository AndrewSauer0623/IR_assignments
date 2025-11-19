# Andrew
from preprocess import preprocess_text, compute_term_frequencies
from index_builder import build_inverted_index, normalize_document_weights
from tree23 import build_permuterm_index_from_terms
from query import find_terms_by_prefix, compute_query_weights, rank_documents


def print_trec_format(ranked_results, query_id: str, run_name: str):
    for rank, (doc_id, score) in enumerate(ranked_results, start=1):
        print(f"{query_id} Q0 {doc_id} {rank} {score:.6f} {run_name}")


def main():
    documents = {
        1: "for english model retireval have a relevance model while vector space model retrieval",
        2: "r-precision measure is relevant to average precision measure",
        3: "most efficient retrieval models are language model and vector space model",
        4: "english is the most efficient language",
        5: "retrieval efficiency is measured by average precision",
    }

    # Preprocess documents
    doc_tokens = {doc_id: preprocess_text(text) for doc_id, text in documents.items()}

    # Compute term frequencies
    term_freqs = compute_term_frequencies(doc_tokens)

    # Build inverted index with weighting
    inverted_index = build_inverted_index(term_freqs)
    inverted_index = normalize_document_weights(inverted_index)

    # Build permuterm index from unique terms
    terms = list(inverted_index.keys())
    perm_root = build_permuterm_index_from_terms(terms)
    query = "c*t"

    # Do NOT preprocess wildcard queries (keep * intact)
    query_tokens = [query]

    # Expand wildcard queries using permuterm index
    expanded_terms = []
    for qt in query_tokens:
        if '*' in qt:
            matches, _ = find_terms_by_prefix(perm_root, qt)
            expanded_terms.extend(matches)
        else:
            # normal terms can still be preprocessed
            expanded_terms.extend(preprocess_text(qt))

    # Compute query weights (ltc scheme)
    q_weights = compute_query_weights(expanded_terms, inverted_index)

    # Rank documents by similarity
    ranked_results = rank_documents(q_weights, inverted_index)

    # Output results in TREC format
    print_trec_format(ranked_results, query_id="1", run_name="test")


if __name__ == "__main__":
    main()
