import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Primary local cross-encoder model (~91MB)
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker_instance = None


def get_reranker_model():
    """Lazy load local CrossEncoder reranking model."""
    global _reranker_instance
    if _reranker_instance is None:
        from sentence_transformers import CrossEncoder
        logger.info(f"Loading local cross-encoder model: {RERANKER_MODEL_NAME}...")
        _reranker_instance = CrossEncoder(RERANKER_MODEL_NAME)
    return _reranker_instance


def rerank_candidates(query: str, candidates: List[Dict[str, Any]], top_k: int = 15) -> List[Dict[str, Any]]:
    """Rerank candidate paper objects using local cross-encoder model.
    Passes (query, paper_text_snippet) pairs through cross-encoder."""
    if not candidates or not query:
        return candidates[:top_k]

    model = get_reranker_model()

    # Form query-passage pairs
    pairs: List[Tuple[str, str]] = []
    for cand in candidates:
        text_passage = f"{cand.get('title', '')} | {cand.get('abstract', '') or cand.get('snippet', '')}"
        pairs.append((query, text_passage))

    scores = model.predict(pairs)

    # Attach cross-encoder scores and sort
    for cand, score in zip(candidates, scores):
        cand["rerank_score"] = round(float(score), 4)

    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]
