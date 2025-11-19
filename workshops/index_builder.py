# Max
from typing import Optional
from tree23 import TreeNode, insert_term
from preprocess import preprocess_text

import math
from collections import defaultdict

def build_inverted_index(term_frequencies):
    inverted_index = {}

    for document_id in term_frequencies:
        term_dict = term_frequencies[document_id]
        for term in term_dict:
            tf = term_dict[term]

            if term not in inverted_index:
                inverted_index[term] = {'df': 0, 'postings': {}}

            log_tf = 0.0
            if tf > 0:
                log_tf = 1 + math.log(tf)

            inverted_index[term]['postings'][document_id] = {
                'tf': tf,
                'log_tf': log_tf
            }

    # Compute document frequency for each term
    for term in inverted_index:
        postings_dict = inverted_index[term]['postings']
        inverted_index[term]['df'] = len(postings_dict)

    return inverted_index


def normalize_document_weights(inverted_index):
    # Compute the sum of squares of log_tf for each document
    document_lengths = defaultdict(float)

    for term in inverted_index:
        postings_dict = inverted_index[term]['postings']
        for document_id in postings_dict:
            log_tf = postings_dict[document_id]['log_tf']
            document_lengths[document_id] += log_tf * log_tf

    # Take square root to get vector length
    for document_id in document_lengths:
        document_lengths[document_id] = math.sqrt(document_lengths[document_id])

    # Normalize each log_tf by document vector length
    for term in inverted_index:
        postings_dict = inverted_index[term]['postings']
        for document_id in postings_dict:
            vector_length = document_lengths[document_id]
            if vector_length > 0:
                normalized_weight = postings_dict[document_id]['log_tf'] / vector_length
            else:
                normalized_weight = 0.0
            postings_dict[document_id]['normalized'] = normalized_weight

    return inverted_index



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
