# Oliwia
class TreeNode:
    def __init__(self, keys=None, children=None):
        self.keys = keys or []             # 1–2 terms
        self.children = children or []     # 0, 2, or 3 child nodes
        self.term_documents = {}           # {term: [document_ids]}

def insert_term(root: TreeNode, term: str, document_id: int) -> TreeNode:
    """
    Input:  tree root, term, document_id
    Output: updated root after insertion
    Behavior: keep tree balanced; add document_id if term already exists
    """

def find_term(root: TreeNode, term: str) -> list[int]:
    """
    Input:  tree root, search term
    Output: list of document IDs containing that term
    """
