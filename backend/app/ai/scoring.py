"""Hallucination detection and confidence scoring engines."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.ai.verification import VerificationResult
from app.schemas import HallucinationRisk, VerificationStatus


@dataclass
class ConfidenceWeights:
    retriever_similarity: float = 0.25
    source_factor: float = 0.20
    evidence_agreement: float = 0.20
    verifier_confidence: float = 0.25
    hallucination_penalty: float = 0.10


DEFAULT_WEIGHTS = ConfidenceWeights()


@dataclass
class ClaimRisk:
    claim: str
    risk_pct: float
    classification: HallucinationRisk
    reasoning: str


@dataclass
class HallucinationReport:
    overall_risk_pct: float
    classification: HallucinationRisk
    claim_risks: list[ClaimRisk] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class ConfidenceReport:
    overall_confidence: float
    claim_confidences: list[float] = field(default_factory=list)
    breakdown: dict[str, float] = field(default_factory=dict)


_STATUS_RISK_MAP: dict[VerificationStatus, float] = {
    VerificationStatus.SUPPORTED: 0.05,
    VerificationStatus.PARTIALLY_SUPPORTED: 0.35,
    VerificationStatus.UNSUPPORTED: 0.85,
    VerificationStatus.CONTRADICTED: 0.95,
}


def classify_claim_risk(verification: VerificationResult) -> ClaimRisk:
    base_risk = _STATUS_RISK_MAP.get(verification.status, 0.5)
    entailment_factor = 1.0 - verification.entailment_score
    verifier_factor = 1.0 - verification.confidence
    risk = min(1.0, (base_risk * 0.5) + (entailment_factor * 0.25) + (verifier_factor * 0.25))
    risk_pct = round(risk * 100, 1)

    if risk_pct <= 20:
        classification = HallucinationRisk.VERIFIED
        reasoning = "Claim is well-supported by retrieved evidence"
    elif risk_pct <= 50:
        classification = HallucinationRisk.LOW_CONFIDENCE
        reasoning = "Claim has partial or limited evidence support"
    else:
        classification = HallucinationRisk.HALLUCINATED
        reasoning = "Claim lacks sufficient evidence or may be fabricated"

    return ClaimRisk(
        claim=verification.claim,
        risk_pct=risk_pct,
        classification=classification,
        reasoning=reasoning,
    )


def detect_hallucinations(
    verifications: list[VerificationResult],
) -> HallucinationReport:
    if not verifications:
        return HallucinationReport(
            overall_risk_pct=100.0,
            classification=HallucinationRisk.HALLUCINATED,
            reasoning="No claims to verify",
        )

    claim_risks = [classify_claim_risk(v) for v in verifications]
    overall = sum(cr.risk_pct for cr in claim_risks) / len(claim_risks)

    if overall <= 20:
        classification = HallucinationRisk.VERIFIED
    elif overall <= 50:
        classification = HallucinationRisk.LOW_CONFIDENCE
    else:
        classification = HallucinationRisk.HALLUCINATED

    supported = sum(1 for v in verifications if v.status == VerificationStatus.SUPPORTED)
    return HallucinationReport(
        overall_risk_pct=round(overall, 1),
        classification=classification,
        claim_risks=claim_risks,
        reasoning=f"{supported}/{len(verifications)} claims fully supported by evidence",
    )


def compute_confidence(
    verifications: list[VerificationResult],
    retrieval_scores: list[float],
    weights: ConfidenceWeights | None = None,
) -> ConfidenceReport:
    w = weights or DEFAULT_WEIGHTS

    avg_retrieval = sum(retrieval_scores) / max(len(retrieval_scores), 1) if retrieval_scores else 0.5
    source_count = len({e.document_id for v in verifications for e in v.evidence if e.document_id})
    source_factor = min(1.0, source_count / 3.0)

    statuses = [v.status for v in verifications]
    supported = sum(1 for s in statuses if s == VerificationStatus.SUPPORTED)
    agreement = supported / max(len(statuses), 1)

    avg_verifier = sum(v.confidence for v in verifications) / max(len(verifications), 1)
    hallucination_report = detect_hallucinations(verifications)
    penalty = hallucination_report.overall_risk_pct / 100.0

    breakdown = {
        "retriever_similarity": round(avg_retrieval, 3),
        "source_factor": round(source_factor, 3),
        "evidence_agreement": round(agreement, 3),
        "verifier_confidence": round(avg_verifier, 3),
        "hallucination_penalty": round(penalty, 3),
    }

    overall = (
        w.retriever_similarity * avg_retrieval
        + w.source_factor * source_factor
        + w.evidence_agreement * agreement
        + w.verifier_confidence * avg_verifier
        - w.hallucination_penalty * penalty
    )
    overall = max(0.0, min(1.0, overall))

    claim_confidences = [round(1.0 - cr.risk_pct / 100.0, 3) for cr in hallucination_report.claim_risks]

    return ConfidenceReport(
        overall_confidence=round(overall, 3),
        claim_confidences=claim_confidences,
        breakdown=breakdown,
    )
