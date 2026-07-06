"""API v1 route handlers."""

from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from app.ai.llm import MODEL_REGISTRY, is_model_available, stream_llm
from app.api.v1.auth import router as auth_router
from app.cache import check_redis_connection, rate_limit_check
from app.config import settings
from app.database import check_db_connection
from app.dependencies import AdminUser, DBSession, OptionalUser
from app.schemas import (
    AdminSettingsResponse,
    AdminSettingsUpdate,
    AskRequest,
    AskResponse,
    BenchmarkRequest,
    BenchmarkResponse,
    EvaluateRequest,
    EvaluateResponse,
    ExtractClaimsRequest,
    ExtractClaimsResponse,
    HealthResponse,
    MetricsResponse,
    ModelInfo,
    ModelsResponse,
    ResearchResponse,
    SourceListResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.services import (
    AdminService,
    AskService,
    BenchmarkService,
    ClaimsService,
    EvaluationService,
    MetricsService,
    ResearchService,
    SourceService,
    VerificationService,
)
from app.ai.embeddings import check_qdrant_connection
from app.utils.audit import log_audit
from app.utils.logger import get_logger
from app.utils.security import detect_prompt_injection

logger = get_logger(__name__)
router = APIRouter()
router.include_router(auth_router)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()
    qdrant_ok = await check_qdrant_connection()
    all_ok = db_ok and redis_ok
    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        version=settings.APP_VERSION,
        database=db_ok,
        redis=redis_ok,
        qdrant=qdrant_ok,
    )


@router.get("/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    models = [
        ModelInfo(
            id=name,
            name=name,
            provider=info["provider"],
            available=is_model_available(name),
        )
        for name, info in MODEL_REGISTRY.items()
    ]
    return ModelsResponse(models=models, default_model=settings.DEFAULT_LLM_MODEL)


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    body: AskRequest,
    db: DBSession,
    user_id: OptionalUser,
    request: Request,
) -> AskResponse | StreamingResponse:
    if detect_prompt_injection(body.question):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid input detected")

    uid = str(user_id or request.client.host if request.client else "anonymous")
    allowed, _, _ = await rate_limit_check(uid, "ask", settings.RATE_LIMIT_ASK)
    if not allowed:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")

    if body.stream:
        return StreamingResponse(
            _stream_ask(body.question, body.model, db, user_id, body.research_mode, request),
            media_type="text/event-stream",
        )

    service = AskService(db)
    result = await service.ask(body.question, body.model, body.research_mode, user_id)

    await log_audit(
        db,
        action="query.ask",
        user_id=user_id,
        resource_type="query",
        resource_id=str(result.query_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"model": body.model, "research_mode": body.research_mode},
    )
    return result


@router.post("/ask/stream")
async def ask_stream(
    body: AskRequest,
    db: DBSession,
    user_id: OptionalUser,
    request: Request,
) -> StreamingResponse:
    """SSE streaming endpoint (alias for POST /ask with stream=true)."""
    body.stream = True
    return await ask_question(body, db, user_id, request)  # type: ignore[return-value]


async def _stream_ask(question, model, db, user_id, research_mode, request=None):
    service = AskService(db)
    result = await service.ask(question, model, research_mode, user_id)

    if request is not None:
        await log_audit(
            db,
            action="query.ask",
            user_id=user_id,
            resource_type="query",
            resource_id=str(result.query_id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"model": model, "research_mode": research_mode, "stream": True},
        )

    for i in range(0, len(result.answer), 20):
        chunk = result.answer[i:i + 20]
        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

    yield f"data: {json.dumps({'type': 'done', 'result': result.model_dump(mode='json')})}\n\n"


@router.get("/ask/{query_id}", response_model=AskResponse)
async def get_query_result(query_id: UUID, db: DBSession) -> AskResponse:
    return await _get_stored_query(query_id, db)


@router.get("/results/{query_id}", response_model=AskResponse)
async def get_result(query_id: UUID, db: DBSession) -> AskResponse:
    """Frontend-compatible alias for GET /ask/{query_id}."""
    return await _get_stored_query(query_id, db)


async def _get_stored_query(query_id: UUID, db: DBSession) -> AskResponse:
    from app.repositories import QueryRepository
    repo = QueryRepository(db)
    query = await repo.get_by_id(query_id)
    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Query not found")

    return await run_pipeline_reconstruct(query)


async def run_pipeline_reconstruct(query) -> AskResponse:
    """Reconstruct AskResponse from stored query."""
    from app.schemas import (
        CitationResponse, ClaimResponse, ConfidenceBreakdownResponse,
        EvidenceSnippet, HallucinationRisk, VerificationStatus,
    )

    claims = [
        ClaimResponse(
            claim=c.claim_text,
            status=VerificationStatus(c.status),
            confidence=c.confidence or 0,
            hallucination_risk=HallucinationRisk.VERIFIED,
            evidence=[
                EvidenceSnippet(
                    source="", excerpt=e.chunk_text,
                    similarity_score=e.similarity_score,
                )
                for e in c.evidence
            ],
            reasoning=c.reasoning,
        )
        for c in query.claims
    ]

    breakdown = None
    if query.confidence_breakdown:
        cb = query.confidence_breakdown
        breakdown = ConfidenceBreakdownResponse(
            retriever_similarity=cb.retriever_similarity or 0,
            source_factor=cb.source_factor or 0,
            evidence_agreement=cb.evidence_agreement or 0,
            verifier_confidence=cb.verifier_confidence or 0,
            hallucination_penalty=cb.hallucination_penalty or 0,
            final_score=cb.final_score or 0,
        )

    return AskResponse(
        query_id=query.id,
        question=query.question,
        answer=query.answer or "",
        insufficient_evidence=query.insufficient_evidence,
        confidence_score=query.confidence_score or 0,
        hallucination_risk_pct=query.hallucination_score or 0,
        hallucination_classification=HallucinationRisk(
            query.hallucination_risk or "Low Confidence",
        ),
        claims=claims,
        citations=[],
        confidence_breakdown=breakdown,
        pipeline_latency_ms=query.pipeline_latency_ms or 0,
        model_used=query.model_used,
    )


@router.post("/extract-claims", response_model=ExtractClaimsResponse)
async def extract_claims_endpoint(body: ExtractClaimsRequest) -> ExtractClaimsResponse:
    service = ClaimsService()
    return await service.extract(body.text, body.model)


@router.post("/verify", response_model=VerifyResponse)
async def verify_claims_endpoint(body: VerifyRequest) -> VerifyResponse:
    service = VerificationService()
    return await service.verify(body.claims, body.context_chunks, body.model)


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_endpoint(
    body: EvaluateRequest, db: DBSession, user_id: OptionalUser,
) -> EvaluateResponse:
    service = EvaluationService(db)
    return await service.evaluate(
        question=body.question, answer=body.answer,
        contexts=body.contexts, framework=body.framework,
        query_id=body.query_id, user_id=user_id,
    )


@router.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark_endpoint(
    body: BenchmarkRequest, db: DBSession, user_id: OptionalUser,
) -> BenchmarkResponse:
    service = BenchmarkService(db)
    return await service.run_benchmark(
        body.name, body.models, body.questions, user_id,
    )


@router.get("/benchmark", response_model=BenchmarkResponse)
async def get_latest_benchmark(db: DBSession) -> BenchmarkResponse:
    service = BenchmarkService(db)
    result = await service.get_latest()
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No benchmark results found")
    return result


@router.get("/research/{query_id}", response_model=ResearchResponse)
async def get_research(query_id: UUID, db: DBSession) -> ResearchResponse:
    service = ResearchService(db)
    try:
        return await service.get_research(query_id)
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get("/admin/settings", response_model=AdminSettingsResponse)
async def get_admin_settings() -> AdminSettingsResponse:
    service = AdminService()
    return await service.get_settings()


@router.put("/admin/settings", response_model=AdminSettingsResponse)
async def update_admin_settings(
    body: AdminSettingsUpdate,
    db: DBSession,
    admin_id: AdminUser,
    request: Request,
) -> AdminSettingsResponse:
    service = AdminService()
    result = await service.update_settings(body)
    await log_audit(
        db,
        action="admin.settings_update",
        user_id=admin_id,
        resource_type="settings",
        details=body.model_dump(exclude_unset=True),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return result


@router.get("/sources", response_model=SourceListResponse)
async def list_sources(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: str | None = None,
    search: str | None = None,
    document_type: str | None = None,
) -> SourceListResponse:
    service = SourceService(db)
    return await service.list_sources(page, page_size, source, search, document_type)


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: DBSession) -> MetricsResponse:
    service = MetricsService(db)
    return await service.get_metrics()


@router.get("/metrics/history")
async def get_metrics_history(db: DBSession) -> list[dict]:
    service = MetricsService(db)
    return await service.get_metrics_history()
