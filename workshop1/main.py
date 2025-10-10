# Andrew
from index_builder import build_document_index
from query import find_terms_by_prefix

documents = {
    1: "At very low temperatures, superconductors have zero resistance, but they can also repel an external magnetic field, in such a way that a spinning magnet can be held in a levitated position.",
    2: "If a small magnet is brought near a superconductor, it will be repelled."
}

index_root = build_document_index(documents)
matches, steps = find_terms_by_prefix(index_root, "s")
print("Matching terms:", matches)
print("Nodes visited:", steps)