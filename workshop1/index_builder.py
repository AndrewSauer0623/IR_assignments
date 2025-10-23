# Max
from typing import Optional
from tree23 import TreeNode, insert_term
from preprocess import preprocess_text

def build_inverted_index(tf_dict):
    """
    Input:  {doc_id: {term: tf}}
    Output: {term: {'df': int, 'postings': {doc_id: {'tf': int, 'log_tf': float}}}}

    For each term:
      - compute document frequency (df)
      - compute log(tf)
      - store tf + log_tf in postings
    """
    pass

def normalize_document_weights(inverted_index):
    """
    Input:  inverted_index (with log_tf)
    Output: inverted_index with normalized weights per doc

    Steps:
      - Compute document vector length (sqrt of sum of squares)
      - Divide each weight by its doc vector length
    """
    pass


def generate_permuterms(term: str) -> list[str]:
    term = term + '$'
    return [term[i:] + term[:i] for i in range(len(term))]

def build_permuterm_index(documents: dict[int, str]) -> Optional[TreeNode]:
    # - integrate TF info later when available (optional)
    # - current build_permuterm_index() logic remains valid
    # - consider linking each permuterm to its base term for faster lookup
    if not documents:
        return None

    root = None
    for doc_id, raw_text in documents.items():
        terms = preprocess_text(raw_text)
        for term in terms:
            for permuterm in generate_permuterms(term):
                root = insert_term(root, permuterm, doc_id)

    return root
