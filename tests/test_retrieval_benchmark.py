import pytest
import time
from proceedings_ingest.lexical_search import search_lexical_bm25
from proceedings_ingest.embeddings import encode_texts, compute_cosine_similarity
from proceedings_ingest.reranker import rerank_candidates

BENCHMARK_QUERIES = [
    "agent-based models for science learning",
    "collaborative problem solving dialogues",
    "epistemic network analysis in medical education",
    "productive failure in conceptual physics",
    "teacher noticing in elementary mathematics",
    "scaffolding self-regulated learning in online environments",
    "multimodal learning analytics and eye tracking",
    "computational thinking in middle school robotics",
    "generative AI and large language models in writing instruction",
    "game-based learning and student engagement"
]

def test_bm25_vs_hybrid_reranking_benchmark():
    print("\n==========================================================")
    print("        LITERATURE REVIEW RETRIEVAL BENCHMARK EVALUATION    ")
    print("==========================================================")

    for q in BENCHMARK_QUERIES:
        start_bm25 = time.time()
        bm25_hits = search_lexical_bm25(q, limit=20, sort_by="relevance")
        bm25_time = (time.time() - start_bm25) * 1000.0

        if not bm25_hits:
            print(f"Query: '{q}' -> 0 BM25 hits ({bm25_time:.1f}ms)")
            continue

        start_rerank = time.time()
        reranked_hits = rerank_candidates(q, list(bm25_hits), top_k=5)
        rerank_time = (time.time() - start_rerank) * 1000.0

        print(f"\nQuery: '{q}'")
        print(f"  BM25 search latency: {bm25_time:.1f}ms | Found: {len(bm25_hits)} candidates")
        print(f"  Reranker latency:    {rerank_time:.1f}ms | Top 5 Reranked:")
        for idx, hit in enumerate(reranked_hits[:3]):
            print(f"    {idx+1}. [{hit['year']}] {hit['title']} (Rerank: {hit['rerank_score']}, BM25: {hit['bm25_score']})")

    assert True
