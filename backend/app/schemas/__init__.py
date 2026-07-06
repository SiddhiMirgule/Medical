"""Pydantic v2 request/response schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


class HallucinationRisk(str, Enum):
    VERIFIED = "Verified"
    LOW_CONFIDENCE = "Low Confidence"
    HALLUCINATED = "Hallucinated"


# ── Ask ────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    model: str | None = None
    stream: bool = False
    research_mode: bool = False


class EvidenceSnippet(BaseModel):
    source: str
    excerpt: str
    pmid: str | None = None
    url: str | None = None
    publication_date: datetime | None = None
    similarity_score: float | None = None
    highlight_start: int | None = None
    highlight_end: int | None = None


class ClaimResponse(BaseModel):
    claim: str
    status: VerificationStatus
    confidence: float
    hallucination_risk: HallucinationRisk
    evidence: list[EvidenceSnippet] = []
    reasoning: str | None = None


class CitationResponse(BaseModel):
    reference_num: int
    title: str
    authors: list[str] = []
    pmid: str | None = None
    url: str | None = None
    publication_date: datetime | None = None
    source: str


class ConfidenceBreakdownResponse(BaseModel):
    retriever_similarity: float
    source_factor: float
    evidence_agreement: float
    verifier_confidence: float
    hallucination_penalty: float
    final_score: float


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    title: str | None = None
    dense_score: float | None = None
    sparse_score: float | None = None
    rrf_score: float | None = None
    rerank_score: float | None = None


class PipelineTraceResponse(BaseModel):
    node_name: str
    latency_ms: int
    model_used: str | None = None
    error: str | None = None


class AskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    query_id: UUID
    question: str
    answer: str
    insufficient_evidence: bool = False
    confidence_score: float
    hallucination_risk_pct: float
    hallucination_classification: HallucinationRisk
    claims: list[ClaimResponse] = []
    citations: list[CitationResponse] = []
    confidence_breakdown: ConfidenceBreakdownResponse | None = None
    pipeline_latency_ms: int
    model_used: str
    research_data: dict[str, Any] | None = None


# ── Claims ─────────────────────────────────────────────────────

class ExtractClaimsRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    model: str | None = None


class ExtractedClaim(BaseModel):
    claim: str
    claim_type: str | None = None


class ExtractClaimsResponse(BaseModel):
    claims: list[ExtractedClaim]
    model_used: str


# ── Verify ─────────────────────────────────────────────────────

class VerifyRequest(BaseModel):
    claims: list[str] = Field(..., min_length=1, max_length=50)
    context_chunks: list[str] | None = None
    model: str | None = None


class ClaimVerification(BaseModel):
    claim: str
    status: VerificationStatus
    confidence: float
    evidence: list[EvidenceSnippet] = []
    reasoning: str | None = None


class VerifyResponse(BaseModel):
    verifications: list[ClaimVerification]
    model_used: str


# ── Evaluate ───────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    query_id: UUID | None = None
    question: str | None = None
    answer: str | None = None
    contexts: list[str] | None = None
    framework: str = "ragas"


class EvaluateResponse(BaseModel):
    evaluation_id: UUID
    framework: str
    faithfulness: float | None = None
    context_precision: float | None = None
    context_recall: float | None = None
    answer_relevancy: float | None = None
    metrics: dict[str, float] = {}


# ── Benchmark ──────────────────────────────────────────────────

class BenchmarkRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    models: list[str] = Field(default=["gpt-4o", "claude-sonnet", "llama-3.1"])
    questions: list[str] | None = None


class BenchmarkModelResult(BaseModel):
    model_name: str
    accuracy: float
    hallucination_rate: float
    faithfulness: float
    avg_latency_ms: float
    total_cost_usd: float


class BenchmarkResponse(BaseModel):
    benchmark_id: UUID
    name: str
    status: str
    results: list[BenchmarkModelResult] = []


# ── Sources ────────────────────────────────────────────────────

class SourceDocument(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    authors: list[str] = []
    source: str
    publication_date: datetime | None = None
    pmid: str | None = None
    url: str | None = None
    abstract: str | None = None
    document_type: str | None = None
    keywords: list[str] = []


class SourceListResponse(BaseModel):
    items: list[SourceDocument]
    total: int
    page: int
    page_size: int


# ── Metrics ────────────────────────────────────────────────────

class MetricsResponse(BaseModel):
    total_queries: int
    avg_confidence: float
    avg_hallucination_rate: float
    verification_success_rate: float
    avg_retrieval_latency_ms: float
    avg_llm_latency_ms: float
    evaluation_history: list[dict[str, Any]] = []
    benchmark_leaderboard: list[dict[str, Any]] = []


# ── Health / Models ────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    database: bool
    redis: bool
    qdrant: bool


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    available: bool


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
    default_model: str


# ── Auth ───────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=8)
    role: str = "user"


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── Admin ──────────────────────────────────────────────────────

class AdminSettingsResponse(BaseModel):
    confidence_formula: str
    retrieval_top_k: int
    rerank_top_k: int
    hallucination_threshold: float
    enable_streaming: bool
    default_model: str


class AdminSettingsUpdate(BaseModel):
    confidence_formula: str | None = None
    retrieval_top_k: int | None = Field(None, ge=1, le=100)
    rerank_top_k: int | None = Field(None, ge=1, le=50)
    hallucination_threshold: float | None = Field(None, ge=0, le=100)
    enable_streaming: bool | None = None
    default_model: str | None = None


# ── Research ───────────────────────────────────────────────────

class ResearchChunkResponse(BaseModel):
    chunk_id: str
    text: str
    similarity_score: float
    rerank_score: float | None = None
    document_id: str
    title: str | None = None


class ResearchResponse(BaseModel):
    query_id: UUID
    question: str
    retrieved_chunks: list[ResearchChunkResponse] = []
    pipeline_traces: list[PipelineTraceResponse] = []
    verifications: list[dict[str, Any]] = []
    hallucination_report: dict[str, Any] | None = None
    confidence_breakdown: dict[str, Any] | None = None
    embedding_model: str
    retrieval_method: str = "hybrid_rrf"
    total_retrieved: int
    total_after_rerank: int
