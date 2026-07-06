"""Unit tests for hybrid retrieval."""

import pytest

from app.ai.retrieval import reciprocal_rank_fusion, _tokenize
from app.ai.embeddings import RetrievedChunk


class TestRetrieval:
    def test_tokenize(self):
        tokens = _tokenize("Metformin lowers blood glucose")
        assert "metformin" in tokens
        assert "glucose" in tokens

    def test_rrf_fusion(self):
        dense = [
            RetrievedChunk("c1", "d1", "text1", "title1", dense_score=0.9),
            RetrievedChunk("c2", "d2", "text2", "title2", dense_score=0.8),
        ]
        sparse = [
            RetrievedChunk("c2", "d2", "text2", "title2", sparse_score=5.0),
            RetrievedChunk("c3", "d3", "text3", "title3", sparse_score=4.0),
        ]
        fused = reciprocal_rank_fusion(dense, sparse)
        assert len(fused) == 3
        assert fused[0].rrf_score > 0

    @pytest.mark.asyncio
    async def test_hybrid_retrieve(self):
        from app.ai.retrieval import hybrid_retrieve
        result = await hybrid_retrieve("metformin side effects", top_k=3)
        assert len(result.chunks) <= 3
        assert result.latency_ms >= 0
