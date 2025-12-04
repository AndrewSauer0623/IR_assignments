import os
import json
import random
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Query
from pydantic import BaseModel
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

app = FastAPI()
load_dotenv()

# API key from environment
approved_key = os.getenv("API_KEY")

# Paths
INDEX_PATH = "/index/faiss_index.index"
DATA_DIR = "/index/pubmed_jsonl"

# Load FAISS index
index = faiss.read_index(INDEX_PATH)
dim = index.d
print(f"FAISS index loaded with {index.ntotal} vectors of dimension {dim}")

# Load all JSONL docs into memory
json_docs = []
for file_name in sorted(os.listdir(DATA_DIR)):
    if not file_name.endswith(".jsonl"):
        continue
    with open(os.path.join(DATA_DIR, file_name), "r", encoding="utf-8") as f:
        for line in f:
            try:
                doc = json.loads(line)
                json_docs.append(doc)
            except json.JSONDecodeError:
                continue
print(f"Loaded {len(json_docs)} documents into memory")

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


# Pydantic model
class QueryRequest(BaseModel):
    text: str
    k: int = 5
    docid: str = None


# Middleware for API key
@app.middleware("http")
async def verify_keys(request: Request, call_next):
    api_key = request.headers.get("x-api-key")
    if api_key != approved_key:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")
    return await call_next(request)


# Query endpoint
@app.post("/query")
def query_index(query: QueryRequest):
    # Embed query
    query_embedding = model.encode(
        query.text,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype('float32')
    query_embedding = np.expand_dims(query_embedding, axis=0)

    # FAISS search
    k = query.k
    scores, indices = index.search(query_embedding, k + 2)  # overfetch in case of skipped docs

    # Collect candidates
    candidates = []
    for score, idx in zip(scores[0], indices[0]):
        if len(candidates) >= k + 2:
            break
        try:
            result = json_docs[idx]
            if query.docid and result.get("id") == query.docid:
                continue
            candidates.append({
                "score": float(score),
                "docid": result.get("id", ""),
                "title": result.get("MedlineCitation.Article.ArticleTitle.ArticleTitle", ""),
                "body": result.get("text", ""),
                "url": result.get("PubmedData.ArticleIdList.ArticleId.ArticleId", "")
            })
        except (IndexError, KeyError, json.JSONDecodeError):
            continue

    # BM25 rerank
    if candidates:
        candidate_texts = [c["body"] for c in candidates if c["body"]]
        tokenized_candidates = [text.split() for text in candidate_texts if text]
        if tokenized_candidates:
            bm25 = BM25Okapi(tokenized_candidates)
            query_tokens = query.text.split()
            bm25_scores = bm25.get_scores(query_tokens)
            for c, s in zip(candidates, bm25_scores):
                c["score"] = round(float(s), 4)

    # Return top 3 after rerank
    results = {i + 1: c for i, c in enumerate(sorted(candidates, key=lambda x: -x["score"])[:3])}
    return results


# Random articles endpoint
@app.get("/random")
def get_random_articles(k: int = Query(default=5, ge=1, le=2000)):
    results = {}
    seen_indices = set()
    count = 0
    while count < k:
        idx = random.randint(0, len(json_docs) - 1)
        if idx in seen_indices:
            continue
        seen_indices.add(idx)
        try:
            doc = json_docs[idx]
            results[count + 1] = {
                "docid": doc.get("id", ""),
                "title": doc.get("MedlineCitation.Article.ArticleTitle.ArticleTitle", ""),
                "body": doc.get("text", ""),
                "url": doc.get("PubmedData.ArticleIdList.ArticleId.ArticleId", "")
            }
            count += 1
        except (KeyError, json.JSONDecodeError):
            continue
    return results
