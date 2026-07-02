"""SQLAlchemy ORM models — Query, Claim, ClaimEvidence, Citation, ConfidenceBreakdown, PipelineTrace."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Query(Base):
    """A single user question through the MedVerify pipeline."""

    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    model_used: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    insufficient_evidence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    hallucination_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    hallucination_risk: Mapped[str | None] = mapped_column(String(10), nullable=True)  # Low|Medium|High
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    pipeline_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_chunks_retrieved: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_chunks_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(UTC), server_default=text("NOW()"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="queries")  # type: ignore[name-defined]  # noqa: F821
    claims: Mapped[list["Claim"]] = relationship(
        "Claim", back_populates="query", cascade="all, delete-orphan",
    )
    citations: Mapped[list["Citation"]] = relationship(
        "Citation", back_populates="query", cascade="all, delete-orphan",
    )
    confidence_breakdown: Mapped["ConfidenceBreakdown | None"] = relationship(
        "ConfidenceBreakdown", back_populates="query", cascade="all, delete-orphan", uselist=False,
    )
    pipeline_traces: Mapped[list["PipelineTrace"]] = relationship(
        "PipelineTrace", back_populates="query", cascade="all, delete-orphan",
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Evaluation", back_populates="query", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Query id={self.id} model={self.model_used!r}>"


class Claim(Base):
    """An atomic factual claim extracted from a generated answer."""

    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # mechanism|side_effect|dosage|contraindication|prevalence|recommendation|other
    claim_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    # SUPPORTED|PARTIALLY_SUPPORTED|UNSUPPORTED|CONTRADICTED
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(UTC), server_default=text("NOW()"),
    )

    # Relationships
    query: Mapped[Query] = relationship("Query", back_populates="claims")
    evidence: Mapped[list["ClaimEvidence"]] = relationship(
        "ClaimEvidence", back_populates="claim", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Claim id={self.id} status={self.status!r}>"


class ClaimEvidence(Base):
    """Evidence chunk supporting or refuting a specific claim."""

    __tablename__ = "claim_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True,
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    highlight_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    highlight_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    qdrant_chunk_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(UTC), server_default=text("NOW()"),
    )

    # Relationships
    claim: Mapped[Claim] = relationship("Claim", back_populates="evidence")
    document: Mapped["Document | None"] = relationship("Document")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<ClaimEvidence id={self.id} claim_id={self.claim_id}>"


class Citation(Base):
    """A formatted document citation referenced in a query answer."""

    __tablename__ = "citations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True,
    )
    reference_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    citation_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    query: Mapped[Query] = relationship("Query", back_populates="citations")
    document: Mapped["Document | None"] = relationship("Document")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<Citation ref=[{self.reference_num}] query_id={self.query_id}>"


class ConfidenceBreakdown(Base):
    """Detailed breakdown of the confidence score formula components."""

    __tablename__ = "confidence_breakdowns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    retriever_similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_factor: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_agreement: Mapped[float | None] = mapped_column(Float, nullable=True)
    verifier_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    hallucination_penalty: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    query: Mapped[Query] = relationship("Query", back_populates="confidence_breakdown")

    def __repr__(self) -> str:
        return f"<ConfidenceBreakdown query_id={self.query_id} score={self.final_score}>"


class PipelineTrace(Base):
    """Per-node execution trace for observability."""

    __tablename__ = "pipeline_traces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    node_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(UTC), server_default=text("NOW()"),
    )

    # Relationships
    query: Mapped[Query] = relationship("Query", back_populates="pipeline_traces")

    def __repr__(self) -> str:
        return f"<PipelineTrace node={self.node_name!r} latency={self.latency_ms}ms>"
