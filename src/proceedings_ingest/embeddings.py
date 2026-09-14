import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Primary local embedding model (lightweight, ~133MB)
MODEL_NAME = "BAAI/bge-small-en-v1.5"

_model_instance = None


def get_embedding_model():
    """Lazy load local sentence-transformer embedding model."""
    global _model_instance
    if _model_instance is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading local embedding model: {MODEL_NAME}...")
        # BGE models require query instruction prefix for best performance
        _model_instance = SentenceTransformer(MODEL_NAME)
    return _model_instance


def encode_texts(texts: List[str], is_query: bool = False) -> np.ndarray:
    """Encode list of text strings into normalized vector embeddings."""
    if not texts:
        return np.array([])

    model = get_embedding_model()
    # BGE query instruction prefix
    if is_query:
        prep_texts = [f"Represent this sentence for searching relevant passages: {t}" for t in texts]
    else:
        prep_texts = texts

    embeddings = model.encode(prep_texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings


def compute_cosine_similarity(query_emb: np.ndarray, doc_embs: np.ndarray) -> np.ndarray:
    """Compute cosine similarities between 1D query vector and 2D matrix of doc vectors."""
    if len(query_emb.shape) == 1:
        query_emb = query_emb.reshape(1, -1)
    # Vectors are normalized, so dot product equals cosine similarity
    sims = np.dot(doc_embs, query_emb.T).flatten()
    return sims
