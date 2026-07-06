"""Evidence verification engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ai.embeddings import RetrievedChunk, dense_search, embed_texts
from app.ai.llm import invoke_llm
from app.schemas import VerificationStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)

VERIFICATION_PROMPT = """You are a medical evidence verifier. Given a claim and evidence passages, classify the claim.

Classifications:
- SUPPORTED: Evidence directly supports the claim
- PARTIALLY_SUPPORTED: Evidence partially supports with caveats
- UNSUPPORTED: No evidence supports the claim
- CONTRADICTED: Evidence contradicts the claim

Claim: {claim}

Evidence:
{evidence}

Respond with JSON: {{"status": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""


@dataclass
class EvidenceItem:
    source: str
    excerpt: str
    pmid: str | None = None
    url: str | None = None
    similarity_score: float | None = None
    highlight_start: int | None = None
    highlight_end: int | None = None
    document_id: str | None = None


@dataclass
class VerificationResult:
    claim: str
    status: VerificationStatus
    confidence: float
    evidence: list[EvidenceItem] = field(default_factory=list)
    reasoning: str | None = None
    entailment_score: float = 0.0


def _compute_entailment(claim: str, evidence_text: str) -> float:
    """Cosine similarity between claim and evidence as entailment proxy."""
    try:
        embeddings = embed_texts([claim, evidence_text])
        import numpy as np
        a, b = np.array(embeddings[0]), np.array(embeddings[1])
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
    except Exception:
        return 0.5


def _find_highlight(excerpt: str, claim: str) -> tuple[int | None, int | None]:
    """Find overlapping span between claim keywords and excerpt."""
    claim_words = set(claim.lower().split())
    words = excerpt.lower().split()
    best_start, best_len, best_overlap = 0, 0, 0
    for i in range(len(words)):
        for j in range(i + 1, min(i + 15, len(words) + 1)):
            span_words = words[i:j]
            overlap = sum(1 for w in span_words if w in claim_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_start = i
                best_len = j - i
    if best_overlap < 2:
        return None, None
    char_start = len(" ".join(words[:best_start])) + (1 if best_start > 0 else 0)
    char_end = char_start + len(" ".join(words[best_start:best_start + best_len]))
    return char_start, char_end


async def verify_claim(
    claim: str,
    context_chunks: list[RetrievedChunk] | None = None,
    model: str | None = None,
) -> VerificationResult:
    """Verify a single claim against retrieved evidence."""
    if context_chunks is None:
        context_chunks = await dense_search(claim, top_k=5)

    evidence_items: list[EvidenceItem] = []
    entailment_scores = []

    for chunk in context_chunks:
        entailment = _compute_entailment(claim, chunk.text)
        entailment_scores.append(entailment)
        hl_start, hl_end = _find_highlight(chunk.text, claim)
        meta = chunk.metadata or {}
        evidence_items.append(EvidenceItem(
            source=str(meta.get("source", "Unknown")),
            excerpt=chunk.text[:500],
            pmid=meta.get("pmid"),
            url=meta.get("url"),
            similarity_score=chunk.rerank_score or chunk.dense_score,
            highlight_start=hl_start,
            highlight_end=hl_end,
            document_id=chunk.document_id,
        ))

    evidence_text = "\n---\n".join(e.excerpt for e in evidence_items[:3])
    prompt = VERIFICATION_PROMPT.format(claim=claim, evidence=evidence_text)
    response = await invoke_llm(prompt, model_name=model)

    status, confidence, reasoning = _parse_verification(response, entailment_scores)

    return VerificationResult(
        claim=claim,
        status=status,
        confidence=confidence,
        evidence=evidence_items,
        reasoning=reasoning,
        entailment_score=max(entailment_scores) if entailment_scores else 0.0,
    )


async def verify_claims(
    claims: list[str],
    context_chunks: list[RetrievedChunk] | None = None,
    model: str | None = None,
) -> list[VerificationResult]:
    results = []
    for claim in claims:
        result = await verify_claim(claim, context_chunks, model)
        results.append(result)
    return results


def _parse_verification(
    response: str,
    entailment_scores: list[float],
) -> tuple[VerificationStatus, float, str]:
    import json
    import re

    avg_entailment = sum(entailment_scores) / max(len(entailment_scores), 1)

    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            data = json.loads(match.group())
            status = VerificationStatus(data.get("status", "UNSUPPORTED"))
            confidence = float(data.get("confidence", avg_entailment))
            reasoning = data.get("reasoning", "")
            return status, confidence, reasoning
    except (json.JSONDecodeError, ValueError):
        pass

    if avg_entailment >= 0.75:
        return VerificationStatus.SUPPORTED, avg_entailment, "High semantic similarity to evidence"
    if avg_entailment >= 0.55:
        return VerificationStatus.PARTIALLY_SUPPORTED, avg_entailment, "Moderate evidence alignment"
    if avg_entailment >= 0.35:
        return VerificationStatus.UNSUPPORTED, avg_entailment, "Insufficient evidence support"
    return VerificationStatus.UNSUPPORTED, avg_entailment, "No supporting evidence found"
