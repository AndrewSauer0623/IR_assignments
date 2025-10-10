# Oliwia
class TreeNode:
    def __init__(self, keys=None, children=None):
        self.keys = keys or []             # holds 1 or 2 keys
        self.children = children or []     # can be 0, 2, or 3 children
        self.term_documents = {}           # maps term -> [document_ids]


def find_term(root: TreeNode, term: str) -> list[int]:
    """
    Input:  tree root, search term
    Output: list of document IDs containing that term
    """
    #if tree is empty, return empty list
    if not root:
        return []

    #check if the current node contains the term
    if term in root.term_documents:
        return root.term_documents[term]

    # f current node is a leaf, term is not in the tree
    if not root.children:
        return []

    #2-node: one key
    if len(root.keys) == 1:
        #go left if term is smaller
        if term < root.keys[0]:
            return find_term(root.children[0], term)
        #go right if term is greater or equal
        else:
            return find_term(root.children[1], term)

    #3-node: two keys
    #go left if smaller than first key
    if term < root.keys[0]:
        return find_term(root.children[0], term)
    #go middle if between keys
    elif term < root.keys[1]:
        return find_term(root.children[1], term)
    #go right if greater or equal to second key
    else:
        return find_term(root.children[2], term)


def insert_term(root: TreeNode, term: str, document_id: int) -> TreeNode:
    """
    Input:  tree root, term, document_id
    Output: updated root after insertion
    Behavior: keep tree balanced; add document_id if term already exists
    """

    #empty tree: create a new root with this term
    if root is None:
        node = TreeNode([term])
        node.term_documents[term] = [document_id]
        return node

    #if term already exists in this node, just add document_id
    if term in root.term_documents:
        if document_id not in root.term_documents[term]:
            root.term_documents[term].append(document_id)
        return root

    #if current node is a leaf, insert term here
    if not root.children:
        root.keys.append(term)
        #keep keys in order
        root.keys.sort()                     
        root.term_documents[term] = [document_id]

        #check for overflow: node now has 3 keys
        if len(root.keys) == 3:
            #split leaf and promote middle key
            return _split_leaf(root)         
        return root

    #internal node: find the correct child to descend
    if len(root.keys) == 1:
        if term < root.keys[0]:
            child_index = 0
        else:
            child_index = 1
    else:
        if term < root.keys[0]:
            child_index = 0
        elif term < root.keys[1]:
            child_index = 1
        else:
            child_index = 2

    #recursively insert term into the chosen child
    root.children[child_index] = insert_term(root.children[child_index], term, document_id)

    #after recursion, check if child overflowed (3 keys)
    if len(root.children[child_index].keys) == 3:
        root = _split_internal(root, child_index)   #handle split and promotion

    return root


def _split_leaf(node: TreeNode) -> TreeNode:
    """Split a leaf with 3 keys into a small root with 2 children."""

    #sort keys to find middle
    keys = sorted(node.keys) 
    #middle key to promote                      
    middle = keys[1]                               

    #create left and right nodes with one key each
    left = TreeNode([keys[0]])
    right = TreeNode([keys[2]])

    #move term->document mapping into new nodes
    left.term_documents[keys[0]] = node.term_documents[keys[0]]
    right.term_documents[keys[2]] = node.term_documents[keys[2]]

    #create new root with promoted middle key
    parent = TreeNode([middle], [left, right])
    parent.term_documents[middle] = node.term_documents[middle]

    return parent


def _split_internal(parent: TreeNode, child_index: int) -> TreeNode:
    """Split an internal child and promote its middle key."""

    child = parent.children[child_index]
    keys = child.keys
    #middle key to promote
    mid_key = keys[1]                             

    #create new left and right nodes with one key each
    left = TreeNode([keys[0]])
    right = TreeNode([keys[2]])

    #move term->document mapping into new nodes
    left.term_documents[keys[0]] = child.term_documents[keys[0]]
    right.term_documents[keys[2]] = child.term_documents[keys[2]]

    #distribute children explicitly to left and right nodes
    if child.children:
        left.children = []
        left.children.append(child.children[0])
        left.children.append(child.children[1])

        right.children = []
        right.children.append(child.children[2])
        right.children.append(child.children[3])

    #create new lists for parent's keys and children after promotion
    new_keys = []
    new_children = []

    for i in range(len(parent.children)):
        if i == child_index:
            #insert promoted key
            new_keys.append(mid_key)   
            #add left child          
            new_children.append(left) 
            #add right child           
            new_children.append(right)           
        else:
            #keep original keys
            new_keys.append(parent.keys[i])   
            #keep original children   
            new_children.append(parent.children[i])  

    parent.keys = new_keys
    parent.children = new_children
    parent.term_documents[mid_key] = child.term_documents[mid_key]

    #if parent now has 3 keys, split it as well 
    if len(parent.keys) == 3:
        return _split_leaf(parent)

    return parent
