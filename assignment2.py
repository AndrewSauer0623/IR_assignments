import re
import sys
from pathlib import Path
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
DOC_RE = re.compile(r"<DOC>(.*?)</DOC>", re.DOTALL | re.IGNORECASE)

def tag_content(tag, text):
    pattern = re.compile(rf"<{tag}>\s*(.*?)\s*</{tag}>", re.DOTALL | re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""

def parse_folder(folder):
    docs = []
    folder_path = Path(folder)
    for file in folder_path.iterdir():
        if file.is_file():
            with open(file, "r", encoding="latin1") as f:
                text = f.read()
            for doc_match in DOC_RE.findall(text):
                docno = tag_content("DOCNO", doc_match)
                headline = tag_content("HEADLINE", doc_match)
                text_body = tag_content("TEXT", doc_match)
                full_text = (headline + " " + text_body).strip()
                if docno and full_text:
                    docs.append((docno, full_text))
    return docs



def tokenize(text):
    raw = re.split(r"[^A-Za-z0-9']+", text)
    tokens = []
    for t in raw:
        t = t.lower()
        if not t:
            continue
        if t.isdigit():
            continue
        if len(t) == 1 and t not in ("a", "i"):
            continue
        tokens.append(t)
    return tokens


def normalize(tokens, stop=True, lemma=True):
    if stop:
        stopset = set(stopwords.words("english"))
    if lemma:
        lemmatizer = WordNetLemmatizer()
    out = []
    for t in tokens:
        if stop and t in stopset:
            continue
        if lemma:
            t = lemmatizer.lemmatize(t, pos="v")
            t = lemmatizer.lemmatize(t, pos="n")
        out.append(t)
    return out


def build_index(docs):
    index = defaultdict(lambda: {"df": 0, "postings": []})
    for docno, text in docs:
        tokens = normalize(tokenize(text))
        unique_terms = sorted(set(tokens))
        for term in unique_terms:
            index[term]["df"] += 1
            index[term]["postings"].append(docno)
    return dict(index)


def generate_permuterms(term):
    term = term + "$"
    return [term[i:] + term[:i] for i in range(len(term))]


class TreeNode:
    def __init__(self, keys=None, children=None):
        self.keys = keys or []
        self.children = children or []
        self.term_documents = {}


def find_term(root, key):
    if not root:
        return []
    if key in root.term_documents:
        return root.term_documents[key]
    if not root.children:
        return []
    if len(root.keys) == 1:
        if key < root.keys[0]:
            return find_term(root.children[0], key)
        else:
            return find_term(root.children[1], key)
    else:
        if key < root.keys[0]:
            return find_term(root.children[0], key)
        elif key < root.keys[1]:
            return find_term(root.children[1], key)
        else:
            return find_term(root.children[2], key)


def insert_term(root, key, value):
    if root is None:
        node = TreeNode([key])
        node.term_documents[key] = value
        return node
    if key in root.term_documents:
        return root
    if not root.children:
        root.keys.append(key)
        root.keys.sort()
        root.term_documents[key] = value
        if len(root.keys) == 3:
            return _split_leaf(root)
        return root
    if len(root.keys) == 1:
        child_index = 0 if key < root.keys[0] else 1
    else:
        if key < root.keys[0]:
            child_index = 0
        elif key < root.keys[1]:
            child_index = 1
        else:
            child_index = 2
    root.children[child_index] = insert_term(root.children[child_index], key, value)
    if len(root.children[child_index].keys) == 3:
        root = _split_internal(root, child_index)
    return root


def _split_leaf(node):
    keys = sorted(node.keys)
    mid = keys[1]
    left = TreeNode([keys[0]])
    right = TreeNode([keys[2]])
    left.term_documents[keys[0]] = node.term_documents[keys[0]]
    right.term_documents[keys[2]] = node.term_documents[keys[2]]
    parent = TreeNode([mid], [left, right])
    parent.term_documents[mid] = node.term_documents[mid]
    return parent


def _split_internal(parent, idx):
    child = parent.children[idx]
    keys = child.keys
    mid = keys[1]
    left = TreeNode([keys[0]])
    right = TreeNode([keys[2]])
    left.term_documents[keys[0]] = child.term_documents[keys[0]]
    right.term_documents[keys[2]] = child.term_documents[keys[2]]
    if child.children:
        left.children = [child.children[0], child.children[1]]
        right.children = [child.children[2], child.children[3]]
    parent.keys.insert(idx, mid)
    parent.children[idx] = left
    parent.children.insert(idx + 1, right)
    parent.term_documents[mid] = child.term_documents[mid]
    if len(parent.keys) == 3:
        return _split_leaf(parent)
    return parent

def wildcard_to_permuterm_key(pattern):
    prefix, suffix = pattern.split('*', 1)
    return suffix + '$' + prefix


def prefix_search(root, prefix, matches):
    if not root:
        return
    for key in root.keys:
        if key.startswith(prefix):
            matches.extend(root.term_documents[key])
    for child in root.children:
        prefix_search(child, prefix, matches)


def wildcard_search(pattern, tree_root, index, docs):
    if '*' not in pattern:
        print("Wildcard must contain '*'")
        return
    perm_key = wildcard_to_permuterm_key(pattern)
    results = []
    prefix_search(tree_root, perm_key, results)
    results = sorted(set(results))
    if not results:
        print("No matching terms.")
        return
    print(f"Wildcard '{pattern}' matched terms:", results)
    for term in results:
        if term in index:
            print(f"Term '{term}' appears in {index[term]['df']} documents.")
            for docid in index[term]['postings']:
                print(" ", docid)


folder = sys.argv[1]
docs = parse_folder(folder)
index = build_index(docs)
print("Parsed", len(docs), "documents")
print("Vocabulary size:", len(index))

# Build permuterm tree
tree_root = None
for term in index:
    perms = generate_permuterms(term)
    for p in perms:
        tree_root = insert_term(tree_root, p, [term])

# Example wildcard queries
print("\nWildcard examples:")
for q in ["*cancer", "canc*", "can*er"]:
    print("\nQuery:", q)
    wildcard_search(q, tree_root, index, docs)

