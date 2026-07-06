"""Unit tests for hallucination detection and confidence scoring."""

import pytest

from app.ai.scoring import compute_confidence, detect_hallucinations
from app.ai.verification import VerificationResult, EvidenceItem
from app.schemas import VerificationStatus, HallucinationRisk


def _make_verification(status: VerificationStatus, confidence: float = 0.9) -> VerificationResult:
    return VerificationResult(
        claim="Test claim",
        status=status,
        confidence=confidence,
        evidence=[EvidenceItem(source="PubMed", excerpt="Supporting evidence text")],
        entailment_score=0.85 if status == VerificationStatus.SUPPORTED else 0.3,
    )


class TestHallucinationDetection:
    def test_supported_claims_low_risk(self):
        verifications = [_make_verification(VerificationStatus.SUPPORTED)]
        report = detect_hallucinations(verifications)
        assert report.overall_risk_pct <= 30
        assert report.classification == HallucinationRisk.VERIFIED

    def test_unsupported_claims_high_risk(self):
        verifications = [_make_verification(VerificationStatus.UNSUPPORTED, 0.2)]
        report = detect_hallucinations(verifications)
        assert report.overall_risk_pct > 50
        assert report.classification == HallucinationRisk.HALLUCINATED

    def test_empty_verifications(self):
        report = detect_hallucinations([])
        assert report.overall_risk_pct == 100.0


class TestConfidenceScoring:
    def test_confidence_with_supported_claims(self):
        verifications = [_make_verification(VerificationStatus.SUPPORTED)]
        report = compute_confidence(verifications, [0.9, 0.85])
        assert report.overall_confidence > 0.5
        assert "retriever_similarity" in report.breakdown

    def test_confidence_penalizes_hallucinations(self):
        supported = [_make_verification(VerificationStatus.SUPPORTED)]
        unsupported = [_make_verification(VerificationStatus.UNSUPPORTED, 0.1)]
        conf_supported = compute_confidence(supported, [0.9])
        conf_unsupported = compute_confidence(unsupported, [0.9])
        assert conf_supported.overall_confidence > conf_unsupported.overall_confidence
