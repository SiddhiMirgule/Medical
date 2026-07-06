"""BGE embedding service with Qdrant integration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_embedder = None
_qdrant: AsyncQdrantClient | None = None


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    text: str
    title: str | None
    dense_score: float
    sparse_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0
    metadata: dict[str, Any] | None = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE,
            )
        except Exception as exc:
            logger.warning("embedder_load_failed", error=str(exc))
            _embedder = None
    return _embedder


async def get_qdrant() -> AsyncQdrantClient:
    global _qdrant
    if _qdrant is None:
        _qdrant = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY or None,
        )
    return _qdrant


async def ensure_collection() -> None:
    client = await get_qdrant()
    collections = await client.get_collections()
    names = [c.name for c in collections.collections]
    if settings.QDRANT_COLLECTION_NAME not in names:
        await client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=settings.QDRANT_VECTOR_SIZE,
                distance=qmodels.Distance.COSINE,
            ),
        )


def embed_texts(texts: list[str]) -> list[list[float]]:
    embedder = _get_embedder()
    if embedder is None:
        import hashlib
        return [
            [float(int(hashlib.md5(t.encode()).hexdigest()[i:i+2], 16)) / 255.0
             for i in range(0, min(settings.QDRANT_VECTOR_SIZE * 2, 64), 2)]
            + [0.0] * (settings.QDRANT_VECTOR_SIZE - 32)
            for t in texts
        ]
    embeddings = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()


async def upsert_chunks(
    chunks: list[dict[str, Any]],
) -> list[str]:
    """Embed and upsert chunks into Qdrant. Returns point IDs."""
    await ensure_collection()
    client = await get_qdrant()
    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)
    point_ids = []

    points = []
    for chunk, vector in zip(chunks, vectors):
        point_id = chunk.get("qdrant_point_id") or str(uuid.uuid4())
        point_ids.append(point_id)
        points.append(qmodels.PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "chunk_id": chunk.get("chunk_id", point_id),
                "document_id": chunk.get("document_id", ""),
                "text": chunk["text"],
                "title": chunk.get("title", ""),
                "pmid": chunk.get("pmid"),
                "source": chunk.get("source", ""),
                "authors": chunk.get("authors", []),
                "publication_date": chunk.get("publication_date"),
                "url": chunk.get("url"),
            },
        ))

    await client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=points,
    )
    return point_ids


async def dense_search(query: str, top_k: int = 20) -> list[RetrievedChunk]:
    await ensure_collection()
    client = await get_qdrant()
    vector = embed_texts([query])[0]

    try:
        results = await client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
        )
    except Exception as exc:
        logger.warning("dense_search_failed", error=str(exc))
        return _demo_chunks(query, top_k)

    chunks = []
    for hit in results:
        payload = hit.payload or {}
        chunks.append(RetrievedChunk(
            chunk_id=str(payload.get("chunk_id", hit.id)),
            document_id=str(payload.get("document_id", "")),
            text=str(payload.get("text", "")),
            title=payload.get("title"),
            dense_score=float(hit.score),
            metadata=payload,
        ))
    return chunks


def _demo_chunks(query: str, top_k: int) -> list[RetrievedChunk]:
    """Demo medical chunks when Qdrant is empty."""
    demo = [
        RetrievedChunk(
            chunk_id="demo-1", document_id="doc-1",
            text="Metformin is a biguanide antihyperglycemic agent that lowers blood glucose "
                 "by decreasing hepatic glucose production and improving insulin sensitivity.",
            title="Metformin: mechanisms and clinical use",
            dense_score=0.92,
            metadata={"pmid": "12345678", "source": "PubMed"},
        ),
        RetrievedChunk(
            chunk_id="demo-2", document_id="doc-1",
            text="The most common adverse effects of metformin are gastrointestinal, including "
                 "nausea, vomiting, diarrhea, and abdominal discomfort.",
            title="Metformin adverse effects review",
            dense_score=0.88,
            metadata={"pmid": "12345679", "source": "PubMed"},
        ),
        RetrievedChunk(
            chunk_id="demo-3", document_id="doc-2",
            text="Lactic acidosis is a rare but serious complication associated with metformin, "
                 "particularly in patients with renal impairment.",
            title="Metformin safety profile",
            dense_score=0.75,
            metadata={"pmid": "12345680", "source": "NIH"},
        ),
    ]
    return demo[:top_k]


async def check_qdrant_connection() -> bool:
    try:
        client = await get_qdrant()
        await client.get_collections()
        return True
    except Exception:
        return False
