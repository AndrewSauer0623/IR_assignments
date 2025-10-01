#!/usr/bin/env python3
# Program created by Andrew Sauer, Russel, Bailey, Max, Oliwia.
# Contains a functions required to read NYT data and form a simple inverted index.
import re
import sys
import json
from pathlib import Path
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

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
            content = file.read_text(encoding="utf8", errors="ignore")
            blocks = DOC_RE.findall(content)
            for block in blocks:
                docno = tag_content("DOCNO", block)
                headline = tag_content("HEADLINE", block)
                body = tag_content("TEXT", block)
                text = (headline + " " + body).strip()
                docs.append((docno, text))
    return docs

def tokenize(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    raw = re.split(r"[^A-Za-z0-9']+", text)
    tokens = []
    for t in raw:
        t = t.lower()
        if not t:
            continue
        if t == "'":
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

def build_index(docs, stop=True, lemma=True):
    index = defaultdict(lambda: {"df": 0, "postings": []})
    for docno, text in docs:
        tokens = tokenize(text)
        tokens = normalize(tokens, stop, lemma)
        unique_terms = sorted(set(tokens))
        for term in unique_terms:
            index[term]["df"] += 1
            index[term]["postings"].append(docno)
    for term in index:
        index[term]["postings"] = sorted(set(index[term]["postings"]))
    return dict(index)

def query_index(term, index_file="index.json", docs=None):
    term = term.lower()
    with open(index_file, "r", encoding="utf8") as f:
        index = json.load(f)

    if term not in index:
        print(f"Term '{term}' not found in index.")
        return
    entry = index[term]
    print(f"Term: '{term}' appears in {entry['df']} documents.\n")
    if docs is None:
        for docid in entry["postings"]:
            print(" ", docid)
        return
    doc_map = {doc[0]: doc[1] for doc in docs}
    for docid in entry["postings"]:
        text = doc_map.get(docid, "")
        sentences = re.split(r'(?<=[.!?])\s+', text)
        found = [s.strip() for s in sentences if term in s.lower()]
        if found:
            print(f"Document: {docid}")
            for s in found:
                print(" ", s)
            print()

def main():
    folder = sys.argv[2]
    docs = parse_folder(folder)

    print("Parsed", len(docs), "documents")
    index = build_index(docs)
    print("Vocabulary size:", len(index))

    count = 0
    for term in index:
        print(term, "->", index[term])
        count += 1
        if count >= 10:
            break
    with open("index.json", "w", encoding="utf8") as f:
        json.dump(index, f, indent=2)

    query_index("America", docs=docs)

main()
