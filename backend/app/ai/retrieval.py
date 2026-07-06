"""Hybrid retrieval: BM25 + Dense + RRF + BGE Reranker."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from app.ai.embeddings import RetrievedChunk, dense_search
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_reranker = None
_bm25_index: dict[str, list[dict[str, Any]]] = defaultdict(list)


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk] = field(default_factory=list)
    dense_count: int = 0
    sparse_count: int = 0
    fusion_method: str = "rrf"
    reranker_used: bool = False
    latency_ms: int = 0


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def _bm25_score(
    query_tokens: list[str],
    doc_tokens: list[str],
    avg_dl: float,
    doc_freqs: dict[str, int],
    total_docs: int,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    dl = len(doc_tokens)
    tf_map: dict[str, int] = defaultdict(int)
    for t in doc_tokens:
        tf_map[t] += 1

    score = 0.0
    for term in query_tokens:
        if term not in tf_map:
            continue
        tf = tf_map[term]
        df = doc_freqs.get(term, 0)
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
        score += idf * tf_norm
    return score


async def sparse_search(query: str, top_k: int = 20) -> list[RetrievedChunk]:
    """BM25 sparse retrieval over in-memory index + demo corpus."""
    from app.ai.embeddings import _demo_chunks

    corpus = _demo_chunks(query, 50)
    for chunk in corpus:
        _bm25_index["default"].append({
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "text": chunk.text,
            "title": chunk.title,
            "metadata": chunk.metadata,
        })

    docs = _bm25_index.get("default", [])
    if not docs:
        return []

    query_tokens = _tokenize(query)
    all_tokens = [_tokenize(d["text"]) for d in docs]
    avg_dl = sum(len(t) for t in all_tokens) / max(len(all_tokens), 1)

    doc_freqs: dict[str, int] = defaultdict(int)
    for tokens in all_tokens:
        for term in set(tokens):
            doc_freqs[term] += 1

    scored = []
    for doc, tokens in zip(docs, all_tokens):
        score = _bm25_score(query_tokens, tokens, avg_dl, doc_freqs, len(docs))
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, doc in scored[:top_k]:
        results.append(RetrievedChunk(
            chunk_id=doc["chunk_id"],
            document_id=doc["document_id"],
            text=doc["text"],
            title=doc.get("title"),
            sparse_score=score,
            metadata=doc.get("metadata"),
        ))
    return results


def reciprocal_rank_fusion(
    dense_results: list[RetrievedChunk],
    sparse_results: list[RetrievedChunk],
    k: int = 60,
) -> list[RetrievedChunk]:
    """Fuse dense and sparse rankings via RRF."""
    scores: dict[str, float] = defaultdict(float)
    chunk_map: dict[str, RetrievedChunk] = {}

    for rank, chunk in enumerate(dense_results):
        scores[chunk.chunk_id] += 1.0 / (k + rank + 1)
        chunk_map[chunk.chunk_id] = chunk

    for rank, chunk in enumerate(sparse_results):
        scores[chunk.chunk_id] += 1.0 / (k + rank + 1)
        if chunk.chunk_id not in chunk_map:
            chunk_map[chunk.chunk_id] = chunk
        else:
            existing = chunk_map[chunk.chunk_id]
            existing.sparse_score = chunk.sparse_score

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for chunk_id, rrf_score in fused:
        chunk = chunk_map[chunk_id]
        chunk.rrf_score = rrf_score
        results.append(chunk)
    return results


def _get_reranker():
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder("BAAI/bge-reranker-large")
        except Exception as exc:
            logger.warning("reranker_load_failed", error=str(exc))
    return _reranker


def rerank(query: str, chunks: list[RetrievedChunk], top_k: int = 10) -> list[RetrievedChunk]:
    """Rerank chunks using BGE cross-encoder."""
    if not chunks:
        return []

    reranker = _get_reranker()
    if reranker is None:
        for i, c in enumerate(chunks[:top_k]):
            c.rerank_score = c.rrf_score or c.dense_score or (1.0 - i * 0.05)
        return chunks[:top_k]

    pairs = [[query, c.text] for c in chunks]
    try:
        scores = reranker.predict(pairs)
        for chunk, score in zip(chunks, scores):
            chunk.rerank_score = float(score)
        chunks.sort(key=lambda c: c.rerank_score, reverse=True)
    except Exception as exc:
        logger.warning("rerank_failed", error=str(exc))

    return chunks[:top_k]


async def hybrid_retrieve(
    query: str,
    top_k: int = 10,
    dense_k: int = 20,
    sparse_k: int = 20,
) -> RetrievalResult:
    """Full hybrid retrieval pipeline."""
    import time
    start = time.perf_counter()

    dense_results = await dense_search(query, top_k=dense_k)
    sparse_results = await sparse_search(query, top_k=sparse_k)
    fused = reciprocal_rank_fusion(dense_results, sparse_results)
    reranked = rerank(query, fused, top_k=top_k)

    elapsed = int((time.perf_counter() - start) * 1000)
    return RetrievalResult(
        chunks=reranked,
        dense_count=len(dense_results),
        sparse_count=len(sparse_results),
        reranker_used=True,
        latency_ms=elapsed,
    )
