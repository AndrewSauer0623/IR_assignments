# Max
from tree23 import TreeNode, insert_term
from preprocess import preprocess_text
def build_document_index(documents: dict[int, str]) -> TreeNode:
    root = None
    for doc_id, raw_text in documents.items():
        terms = preprocess_text(raw_text)

        for term in terms:
            root = insert_term(root, term, doc_id)

    return root
