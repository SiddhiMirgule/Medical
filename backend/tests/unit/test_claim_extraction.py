"""Unit tests for claim extraction."""

import pytest

from app.ai.claim_extraction import _heuristic_extract, _parse_claims_response


class TestClaimExtraction:
    def test_parse_json_claims(self):
        response = '[{"claim": "Metformin lowers blood glucose"}, {"claim": "Metformin may cause nausea"}]'
        claims = _parse_claims_response(response)
        assert len(claims) == 2
        assert claims[0].claim == "Metformin lowers blood glucose"

    def test_heuristic_extract(self):
        text = "Metformin lowers blood glucose. It may cause nausea."
        claims = _heuristic_extract(text)
        assert len(claims) >= 1

    @pytest.mark.asyncio
    async def test_extract_claims_integration(self):
        from app.ai.claim_extraction import extract_claims
        claims = await extract_claims(
            "Metformin lowers blood glucose and may cause nausea."
        )
        assert len(claims) >= 1
