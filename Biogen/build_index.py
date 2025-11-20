# build_index.py
from typing import List, Tuple
import glob
import json
import os
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import faiss
from structures import Doc
import torch

def load_jsonl(jsonl_dir: str) -> List[Doc]:
    docs: List[Doc] = []
    for path in sorted(glob.glob(os.path.join(jsonl_dir, "*.jsonl"))):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                article = json.loads(line)
                doc = Doc(
                    id=article.get("id", ""),
                    title=article.get("title", ""),
                    text=article.get("text", ""),
                    authors=article.get("authors"),
                    journal=article.get("journal"),
                    pub_date=article.get("pub_date")
                )
                if doc.text:
                    docs.append(doc)
    return docs

def tokenize_docs(docs: List[Doc]) -> List[List[str]]:
    return [(doc.title + " " + doc.text).split() for doc in docs]


def build_bm25(tokenized_docs: List[List[str]]) -> BM25Okapi:
    return BM25Okapi(tokenized_docs)

def query_bm25(query_text: str, bm25: BM25Okapi, docs: List[Doc], top_n: int = 10) -> List[Doc]:
    tokenized_query = query_text.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = scores.argsort()[-top_n:][::-1]
    results = []
    for i in top_indices:
        doc = docs[i]
        doc.score = float(scores[i])
        results.append(doc)
    return results

def build_faiss_index(docs: List[Doc],
                      model_name: str = "all-MiniLM-L6-v2",
                      batch_size: int = 1024,
                      save_dir: str = "faiss_chunks") -> Tuple[faiss.IndexFlatIP, np.ndarray]:
    os.makedirs(save_dir, exist_ok=True)
    model = SentenceTransformer(model_name)

    all_embeddings: List[np.ndarray] = []
    dim = None
    index = None

    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i:i + batch_size]
        texts = [doc.title + " " + doc.text for doc in batch_docs]
        batch_embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

        # attach embeddings to docs
        for j, doc in enumerate(batch_docs):
            doc.embedding = batch_embeddings[j]

        # save batch to disk (crash-safe)
        np.save(os.path.join(save_dir, f"embeddings_batch_{i // batch_size}.npy"), batch_embeddings)

        if index is None:
            dim = batch_embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)

        index.add(batch_embeddings)
        all_embeddings.append(batch_embeddings)

    all_embeddings_np = np.vstack(all_embeddings)
    return index, all_embeddings_np

def save_faiss_index(faiss_index: faiss.Index, file_path: str) -> None:
    faiss.write_index(faiss_index, file_path)


def load_faiss_index(file_path: str) -> faiss.Index:
    return faiss.read_index(file_path)


def query_faiss(query_text: str, faiss_index: faiss.Index, docs: List[Doc],
                model_name: str = "all-MiniLM-L6-v2", top_k: int = 1000) -> List[Doc]:
    device = "mps" if torch.backends.mps.is_built() else "cpu"
    model = SentenceTransformer(model_name, device=device)
    query_vec = model.encode([query_text], convert_to_numpy=True)
    D, I = faiss_index.search(query_vec, top_k)
    results = [docs[i] for i in I[0]]
    for i, doc in enumerate(results):
        doc.score = float(D[0][i])
    return results
