# Max
from 23tree import TreeNode, insert_term
from preprocess import preprocess_text
def build_document_index(documents: dict[int, str]) -> TreeNode:
    """
    Input:  {document_id: raw_text}
    Output: root node of the 2-3 tree mapping terms → document_id lists
    Steps:
        1. For each document, preprocess text to get term list.
        2. Insert each term with its document_id into the tree.
    """
