import os
import json
import random
import numpy as np
from fastapi import FastAPI, HTTPException, Request, Query
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

# API key from environment
API_KEY = os.getenv("API_KEY")

# Paths
INDEX_PATH = "/index/faiss_index.index"
DATA_DIR = "/index/pubmed_jsonl/"

# Load FAISS index
index = faiss.read_index(INDEX_PATH)

# Load all JSONL docs into RAM
docs = []
for fname in sorted(os.listdir(DATA_DIR)):
    if fname.endswith(".jsonl"):
        with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
            for line in f:
                try:
                    docs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

# Sentence Transformer for FAISS queries
model = SentenceTransformer("all-MiniLM-L6-v2")

# Pydantic request model
class QueryRequest(BaseModel):
    text: str
    k_candidates: int = 10  # number of FAISS candidates to fetch
    docid: str = ""          # doc to skip if present

# Middleware for API key check
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")
    return await call_next(request)

# POST /query endpoint
@app.post("/query")
def query_docs(req: QueryRequest):
    # Encode query for FAISS
    query_vec = model.encode([req.text], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    
    # FAISS search for requested number of candidates
    scores, indices = index.search(query_vec, req.k_candidates)

    # Collect FAISS candidate docs
    candidates = []
    candidate_texts = []
    for idx in indices[0]:
        try:
            doc = docs[idx]
            if req.docid and doc.get("docid") == req.docid:
                continue
            candidates.append(doc)
            candidate_texts.append((doc.get("title","") + " " + doc.get("body","")).split())
        except IndexError:
            continue

    if not candidates:
        return {}

    # BM25 rerank over FAISS candidates
    bm25_index = BM25Okapi(candidate_texts)
    bm25_scores = bm25_index.get_scores(req.text.split())

    # Return top 3 reranked results
    top_indices = bm25_scores.argsort()[-3:][::-1]

    results = {}
    for rank, i in enumerate(top_indices):
        doc = candidates[i]
        results[rank+1] = {
            "score": round(float(bm25_scores[i]), 4),
            "docid": doc.get("docid"),
            "title": doc.get("title"),
            "url": doc.get("url"),
            "body": doc.get("body")
        }
    return results

# GET /random endpoint
@app.get("/random")
def random_docs(k: int = Query(default=5, ge=1, le=2000)):
    results = {}
    seen = set()
    count = 0
    while count < k:
        idx = random.randint(0, len(docs) - 1)
        if idx in seen:
            continue
        seen.add(idx)
        doc = docs[idx]
        results[count+1] = {
            "docid": doc.get("docid"),
            "title": doc.get("title"),
            "url": doc.get("url"),
            "body": doc.get("body")
        }
        count += 1
    return results
