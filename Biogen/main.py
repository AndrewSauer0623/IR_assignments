from build_index import *
from preprocess import preprocess_query
from llm_answering import answer_docs_with_llm
from report_gen import generate_biogen_report
from typing import List, Dict
import nltk
import numpy as np
import faiss
import os

def run_pipeline(
        jsonl_dir: str,
        narrative: str,
        faiss_index_file: str = "faiss_index.index",
        top_n_faiss: int = 10,
        top_k_bm25: int = 3,
        max_docs: int = 40,
        question_id: str = "Q1",
        report_file: str = "biogen_report.json") -> None:

    print("Loading JSONL documents...")
    docs = load_jsonl(jsonl_dir)[:max_docs]  # restrict to first max_docs docs
    doc_lookup = {doc.id: doc for doc in docs}  # build lookup for metadata
    print("Loaded", len(docs), "documents")

    # build or load FAISS index
    if os.path.exists(faiss_index_file):
        print("Loading existing FAISS index...")
        full_index = load_faiss_index(faiss_index_file)

        # create a mini index with just the first max_docs vectors
        dim = full_index.d
        faiss_index = faiss.IndexFlatIP(dim)
        vectors = np.vstack([full_index.reconstruct(i) for i in range(max_docs)])
        faiss_index.add(vectors)

        print(f"Mini FAISS index with first {max_docs} vectors loaded")
    else:
        print("Building FAISS index on full corpus...")
        faiss_index, _ = build_faiss_index(docs)
        save_faiss_index(faiss_index, faiss_index_file)
        print("FAISS index built and saved")

    print("Preprocessing query...")
    query_text = preprocess_query(narrative)
    print("Query preprocessing complete")

    print(f"Querying FAISS top {top_n_faiss} documents...")
    faiss_top = query_faiss(query_text, faiss_index, docs, top_k=top_n_faiss)
    print("FAISS query complete")

    print(f"Building BM25 index on FAISS top {top_n_faiss} candidates...")
    tokenized = tokenize_docs(faiss_top)
    bm25 = build_bm25(tokenized)
    print("BM25 index on FAISS candidates built")

    print(f"Reranking top {top_k_bm25} documents with BM25...")
    final_top = query_bm25(query_text, bm25, faiss_top, top_n=top_k_bm25)
    print("BM25 reranking complete")

    print("Sending top documents to LLM for answering...")
    llm_responses = answer_docs_with_llm(final_top)
    print("LLM answering complete")

    print("Generating Biogen report...")
    generate_biogen_report(responses=llm_responses,
                           question_id=question_id,
                           doc_lookup=doc_lookup,
                           output_file=report_file)
    print(f"Pipeline execution complete. Report saved to {report_file}")


if __name__ == "__main__":
    narrative = (
        "Question: What are common mechanisms by which cancer cells develop resistance to chemotherapy drugs?"
        "Narrative: The patient is interested in understanding how cancer cells can evade the effects of chemotherapy treatments. Provide a detailed overview of the biological mechanisms, including genetic mutations, efflux pumps, DNA repair pathways, and changes in cell signaling that contribute to chemotherapy resistance. Focus on general principles rather than any one specific cancer type."
    )
    jsonl_dir = "biogen_data_sample/pubmed_jsonls"

    print("Starting pipeline execution...")
    run_pipeline(jsonl_dir, narrative)
