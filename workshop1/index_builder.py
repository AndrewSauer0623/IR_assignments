from typing import Optional
from tree23 import TreeNode, insert_term
from preprocess import preprocess_text

def generate_permuterms(term: str) -> list[str]:
    term = term + '$'
    return [term[i:] + term[:i] for i in range(len(term))]

def build_permuterm_index(documents: dict[int, str]) -> Optional[TreeNode]:
    if not documents:
        return None

    root = None
    for doc_id, raw_text in documents.items():
        terms = preprocess_text(raw_text)
        for term in terms:
            for permuterm in generate_permuterms(term):
                root = insert_term(root, permuterm, doc_id)

    return root
