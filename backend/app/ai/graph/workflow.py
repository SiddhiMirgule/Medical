"""LangGraph medical QA workflow."""

from __future__ import annotations

import time
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.ai.claim_extraction import extract_claims
from app.ai.embeddings import RetrievedChunk
from app.ai.llm import invoke_llm
from app.ai.retrieval import hybrid_retrieve
from app.ai.scoring import compute_confidence, detect_hallucinations
from app.ai.verification import verify_claims
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

ANSWER_SYSTEM = """You are MedVerify AI, an evidence-grounded medical information assistant.

STRICT RULES:
1. Answer ONLY using the provided evidence passages
2. NEVER fabricate facts, citations, or PMIDs
3. If evidence is insufficient, respond EXACTLY: "Insufficient evidence found."
4. Cite sources using [1], [2] notation matching the evidence list
5. Use cautious medical language (may, commonly, typically)
6. Never provide personal medical advice"""

ANSWER_PROMPT = """Question: {question}

Evidence Passages:
{context}

Provide a clear, evidence-based answer citing sources by number."""


class PipelineState(TypedDict, total=False):
    question: str
    model: str
    research_mode: bool
    processed_query: str
    retrieved_chunks: list[dict]
    context_text: str
    answer: str
    insufficient_evidence: bool
    claims: list[dict]
    verifications: list[dict]
    hallucination_report: dict
    confidence_report: dict
    citations: list[dict]
    pipeline_traces: list[dict]
    research_data: dict
    total_latency_ms: int


async def process_query(state: PipelineState) -> PipelineState:
    start = time.perf_counter()
    question = state["question"].strip()
    traces = state.get("pipeline_traces", [])
    traces.append({
        "node_name": "query_processing",
        "latency_ms": int((time.perf_counter() - start) * 1000),
    })
    return {**state, "processed_query": question, "pipeline_traces": traces}


async def retrieve_evidence(state: PipelineState) -> PipelineState:
    start = time.perf_counter()
    traces = state.get("pipeline_traces", [])

    result = await hybrid_retrieve(state["processed_query"], top_k=10)
    chunks_data = [
        {
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "text": c.text,
            "title": c.title,
            "dense_score": c.dense_score,
            "sparse_score": c.sparse_score,
            "rrf_score": c.rrf_score,
            "rerank_score": c.rerank_score,
            "metadata": c.metadata,
        }
        for c in result.chunks
    ]

    context_parts = []
    for i, c in enumerate(result.chunks, 1):
        title = c.title or "Unknown"
        context_parts.append(f"[{i}] {title}\n{c.text}")

    traces.append({
        "node_name": "hybrid_retrieval",
        "latency_ms": result.latency_ms,
    })
    return {
        **state,
        "retrieved_chunks": chunks_data,
        "context_text": "\n\n".join(context_parts),
        "pipeline_traces": traces,
    }


async def generate_answer(state: PipelineState) -> PipelineState:
    start = time.perf_counter()
    traces = state.get("pipeline_traces", [])

    if not state.get("context_text"):
        return {
            **state,
            "answer": "Insufficient evidence found.",
            "insufficient_evidence": True,
            "pipeline_traces": traces + [{
                "node_name": "answer_generation",
                "latency_ms": int((time.perf_counter() - start) * 1000),
                "model_used": state.get("model", settings.DEFAULT_LLM_MODEL),
            }],
        }

    prompt = ANSWER_PROMPT.format(
        question=state["processed_query"],
        context=state["context_text"],
    )
    answer = await invoke_llm(prompt, system=ANSWER_SYSTEM, model_name=state.get("model"))
    insufficient = "insufficient evidence" in answer.lower()

    traces.append({
        "node_name": "answer_generation",
        "latency_ms": int((time.perf_counter() - start) * 1000),
        "model_used": state.get("model", settings.DEFAULT_LLM_MODEL),
    })
    return {**state, "answer": answer, "insufficient_evidence": insufficient, "pipeline_traces": traces}


async def extract_claims_node(state: PipelineState) -> PipelineState:
    start = time.perf_counter()
    traces = state.get("pipeline_traces", [])

    if state.get("insufficient_evidence"):
        return {**state, "claims": [], "pipeline_traces": traces}

    claims = await extract_claims(state["answer"], model=state.get("model"))
    claims_data = [{"claim": c.claim, "claim_type": c.claim_type} for c in claims]

    traces.append({
        "node_name": "claim_extraction",
        "latency_ms": int((time.perf_counter() - start) * 1000),
    })
    return {**state, "claims": claims_data, "pipeline_traces": traces}


async def verify_evidence(state: PipelineState) -> PipelineState:
    start = time.perf_counter()
    traces = state.get("pipeline_traces", [])

    chunks = [
        RetrievedChunk(
            chunk_id=c["chunk_id"],
            document_id=c["document_id"],
            text=c["text"],
            title=c.get("title"),
            dense_score=c.get("dense_score", 0),
            rerank_score=c.get("rerank_score"),
            metadata=c.get("metadata"),
        )
        for c in state.get("retrieved_chunks", [])
    ]

    claim_texts = [c["claim"] for c in state.get("claims", [])]
    if not claim_texts:
        return {**state, "verifications": [], "pipeline_traces": traces}

    results = await verify_claims(claim_texts, chunks, model=state.get("model"))
    verifications_data = [
        {
            "claim": r.claim,
            "status": r.status.value,
            "confidence": r.confidence,
            "reasoning": r.reasoning,
            "entailment_score": r.entailment_score,
            "evidence": [
                {
                    "source": e.source,
                    "excerpt": e.excerpt,
                    "pmid": e.pmid,
                    "url": e.url,
                    "similarity_score": e.similarity_score,
                    "highlight_start": e.highlight_start,
                    "highlight_end": e.highlight_end,
                    "document_id": e.document_id,
                }
                for e in r.evidence
            ],
        }
        for r in results
    ]

    traces.append({
        "node_name": "evidence_verification",
        "latency_ms": int((time.perf_counter() - start) * 1000),
    })
    return {**state, "verifications": verifications_data, "pipeline_traces": traces}


async def score_response(state: PipelineState) -> PipelineState:
    start = time.perf_counter()
    traces = state.get("pipeline_traces", [])

    from app.ai.verification import VerificationResult, EvidenceItem
    from app.schemas import VerificationStatus

    verifications = []
    for v in state.get("verifications", []):
        verifications.append(VerificationResult(
            claim=v["claim"],
            status=VerificationStatus(v["status"]),
            confidence=v["confidence"],
            reasoning=v.get("reasoning"),
            entailment_score=v.get("entailment_score", 0),
            evidence=[
                EvidenceItem(**{k: ev.get(k) for k in [
                    "source", "excerpt", "pmid", "url",
                    "similarity_score", "highlight_start", "highlight_end", "document_id",
                ]})
                for ev in v.get("evidence", [])
            ],
        ))

    retrieval_scores = [
        c.get("rerank_score") or c.get("dense_score", 0)
        for c in state.get("retrieved_chunks", [])
    ]

    hallucination = detect_hallucinations(verifications)
    confidence = compute_confidence(verifications, retrieval_scores)

    citations = _build_citations(state.get("retrieved_chunks", []))

    research_data = {}
    if state.get("research_mode"):
        research_data = {
            "retrieved_chunks": state.get("retrieved_chunks", []),
            "pipeline_traces": traces,
            "verifications": state.get("verifications", []),
            "hallucination_report": {
                "overall_risk_pct": hallucination.overall_risk_pct,
                "classification": hallucination.classification.value,
                "claim_risks": [
                    {"claim": cr.claim, "risk_pct": cr.risk_pct,
                     "classification": cr.classification.value}
                    for cr in hallucination.claim_risks
                ],
            },
            "confidence_breakdown": confidence.breakdown,
        }

    traces.append({
        "node_name": "scoring",
        "latency_ms": int((time.perf_counter() - start) * 1000),
    })

    return {
        **state,
        "hallucination_report": {
            "overall_risk_pct": hallucination.overall_risk_pct,
            "classification": hallucination.classification.value,
            "reasoning": hallucination.reasoning,
        },
        "confidence_report": {
            "overall_confidence": confidence.overall_confidence,
            "breakdown": confidence.breakdown,
        },
        "citations": citations,
        "research_data": research_data,
        "pipeline_traces": traces,
    }


def _build_citations(chunks: list[dict]) -> list[dict]:
    seen: set[str] = set()
    citations = []
    for i, chunk in enumerate(chunks, 1):
        doc_id = chunk.get("document_id", "")
        if doc_id in seen:
            continue
        seen.add(doc_id)
        meta = chunk.get("metadata") or {}
        citations.append({
            "reference_num": len(citations) + 1,
            "document_id": doc_id,
            "title": chunk.get("title") or meta.get("title", "Unknown"),
            "authors": meta.get("authors", []),
            "pmid": meta.get("pmid"),
            "url": meta.get("url"),
            "source": meta.get("source", "Unknown"),
            "citation_text": f"{chunk.get('title', 'Unknown')} [{meta.get('source', '')}]",
        })
    return citations


def build_medverify_graph() -> StateGraph:
    graph = StateGraph(PipelineState)
    graph.add_node("process_query", process_query)
    graph.add_node("retrieve", retrieve_evidence)
    graph.add_node("generate", generate_answer)
    graph.add_node("extract_claims", extract_claims_node)
    graph.add_node("verify", verify_evidence)
    graph.add_node("score", score_response)

    graph.set_entry_point("process_query")
    graph.add_edge("process_query", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "extract_claims")
    graph.add_edge("extract_claims", "verify")
    graph.add_edge("verify", "score")
    graph.add_edge("score", END)

    return graph


_compiled_graph = None


def get_pipeline():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_medverify_graph().compile()
    return _compiled_graph


async def run_pipeline(
    question: str,
    model: str | None = None,
    research_mode: bool = False,
) -> dict[str, Any]:
    """Execute the full MedVerify LangGraph pipeline."""
    start = time.perf_counter()
    pipeline = get_pipeline()
    initial_state: PipelineState = {
        "question": question,
        "model": model or settings.DEFAULT_LLM_MODEL,
        "research_mode": research_mode,
        "pipeline_traces": [],
    }
    result = await pipeline.ainvoke(initial_state)
    result["total_latency_ms"] = int((time.perf_counter() - start) * 1000)
    return result
