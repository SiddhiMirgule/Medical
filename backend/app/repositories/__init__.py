"""Data access layer — repository pattern."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document, DocumentChunk
from app.models.evaluation import Benchmark, BenchmarkRun, Evaluation
from app.models.query import (
    Citation,
    Claim,
    ClaimEvidence,
    ConfidenceBreakdown,
    PipelineTrace,
    Query,
)
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str, role: str = "user") -> User:
        user = User(email=email, password_hash=password_hash, role=role)
        self.db.add(user)
        await self.db.flush()
        return user


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, doc_id: UUID) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        source: str | None = None,
        search: str | None = None,
        document_type: str | None = None,
    ) -> tuple[list[Document], int]:
        query = select(Document)
        count_query = select(func.count()).select_from(Document)

        if source:
            query = query.where(Document.source == source)
            count_query = count_query.where(Document.source == source)
        if document_type:
            query = query.where(Document.document_type == document_type)
            count_query = count_query.where(Document.document_type == document_type)
        if search:
            pattern = f"%{search}%"
            filt = Document.title.ilike(pattern) | Document.abstract.ilike(pattern)
            query = query.where(filt)
            count_query = count_query.where(filt)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Document.publication_date.desc().nullslast())
            .offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), int(total)

    async def get_by_pmid(self, pmid: str) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.pmid == pmid))
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self.db.add(doc)
        await self.db.flush()
        return doc


class QueryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, query_id: UUID) -> Query | None:
        result = await self.db.execute(
            select(Query)
            .options(
                selectinload(Query.claims).selectinload(Claim.evidence),
                selectinload(Query.citations),
                selectinload(Query.confidence_breakdown),
                selectinload(Query.pipeline_traces),
            )
            .where(Query.id == query_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Query:
        q = Query(**kwargs)
        self.db.add(q)
        await self.db.flush()
        return q

    async def save_claims(self, query_id: UUID, claims_data: list[dict]) -> list[Claim]:
        claims = []
        for i, data in enumerate(claims_data):
            claim = Claim(
                query_id=query_id,
                claim_text=data["claim"],
                claim_type=data.get("claim_type"),
                claim_order=i,
                status=data.get("status", "UNSUPPORTED"),
                confidence=data.get("confidence"),
                reasoning=data.get("reasoning"),
            )
            self.db.add(claim)
            await self.db.flush()

            for ev in data.get("evidence", []):
                self.db.add(ClaimEvidence(
                    claim_id=claim.id,
                    document_id=ev.get("document_id"),
                    chunk_text=ev.get("excerpt", ev.get("chunk_text", "")),
                    highlight_start=ev.get("highlight_start"),
                    highlight_end=ev.get("highlight_end"),
                    similarity_score=ev.get("similarity_score"),
                    qdrant_chunk_id=ev.get("qdrant_chunk_id"),
                ))
            claims.append(claim)
        return claims

    async def save_citations(self, query_id: UUID, citations_data: list[dict]) -> None:
        for c in citations_data:
            self.db.add(Citation(
                query_id=query_id,
                document_id=c.get("document_id"),
                reference_num=c.get("reference_num"),
                citation_text=c.get("citation_text"),
            ))

    async def save_confidence_breakdown(self, query_id: UUID, breakdown: dict) -> None:
        self.db.add(ConfidenceBreakdown(query_id=query_id, **breakdown))

    async def save_pipeline_traces(self, query_id: UUID, traces: list[dict]) -> None:
        for i, t in enumerate(traces):
            self.db.add(PipelineTrace(
                query_id=query_id,
                node_name=t["node_name"],
                node_order=i,
                latency_ms=t.get("latency_ms"),
                model_used=t.get("model_used"),
                error=t.get("error"),
            ))

    async def count_total(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Query))
        return int(result.scalar() or 0)

    async def avg_confidence(self) -> float:
        result = await self.db.execute(
            select(func.avg(Query.confidence_score)).where(Query.confidence_score.isnot(None))
        )
        return float(result.scalar() or 0.0)

    async def avg_hallucination(self) -> float:
        result = await self.db.execute(
            select(func.avg(Query.hallucination_score)).where(Query.hallucination_score.isnot(None))
        )
        return float(result.scalar() or 0.0)


class EvaluationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> Evaluation:
        ev = Evaluation(**kwargs)
        self.db.add(ev)
        await self.db.flush()
        return ev

    async def list_recent(self, limit: int = 50) -> list[Evaluation]:
        result = await self.db.execute(
            select(Evaluation).order_by(Evaluation.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())


class BenchmarkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> Benchmark:
        b = Benchmark(**kwargs)
        self.db.add(b)
        await self.db.flush()
        return b

    async def get_by_id(self, benchmark_id: UUID) -> Benchmark | None:
        result = await self.db.execute(
            select(Benchmark)
            .options(selectinload(Benchmark.runs))
            .where(Benchmark.id == benchmark_id)
        )
        return result.scalar_one_or_none()

    async def save_run(self, benchmark_id: UUID, **kwargs) -> BenchmarkRun:
        run = BenchmarkRun(benchmark_id=benchmark_id, **kwargs)
        self.db.add(run)
        await self.db.flush()
        return run

    async def leaderboard(self, limit: int = 10) -> list[BenchmarkRun]:
        result = await self.db.execute(
            select(BenchmarkRun)
            .where(BenchmarkRun.accuracy.isnot(None))
            .order_by(BenchmarkRun.accuracy.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest(self) -> Benchmark | None:
        result = await self.db.execute(
            select(Benchmark)
            .options(selectinload(Benchmark.runs))
            .where(Benchmark.status == "completed")
            .order_by(Benchmark.completed_at.desc().nullslast(), Benchmark.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
