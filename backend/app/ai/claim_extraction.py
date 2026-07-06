"""Claim extraction service."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.ai.llm import invoke_llm
from app.utils.logger import get_logger

logger = get_logger(__name__)

CLAIM_EXTRACTION_PROMPT = """You are a medical claim extraction system. Decompose the following text into atomic factual claims.

Rules:
- Each claim must be a single, verifiable factual statement
- Preserve medical terminology accurately
- Do not add information not present in the text
- Return ONLY a JSON array of objects with "claim" and optional "claim_type" fields
- claim_type: mechanism|side_effect|dosage|contraindication|prevalence|recommendation|other

Text:
{text}

JSON array:"""


@dataclass
class ExtractedClaim:
    claim: str
    claim_type: str | None = None


async def extract_claims(text: str, model: str | None = None) -> list[ExtractedClaim]:
    """Extract atomic factual claims from generated answer text."""
    prompt = CLAIM_EXTRACTION_PROMPT.format(text=text)
    response = await invoke_llm(
        prompt,
        system="You extract atomic medical claims. Return only valid JSON.",
        model_name=model,
    )

    claims = _parse_claims_response(response)
    if not claims:
        claims = _heuristic_extract(text)
    return claims


def _parse_claims_response(response: str) -> list[ExtractedClaim]:
    try:
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            return []
        data = json.loads(match.group())
        return [
            ExtractedClaim(
                claim=item["claim"] if isinstance(item, dict) else str(item),
                claim_type=item.get("claim_type") if isinstance(item, dict) else None,
            )
            for item in data
        ]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def _heuristic_extract(text: str) -> list[ExtractedClaim]:
    """Fallback: split on sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [
        ExtractedClaim(claim=s.strip())
        for s in sentences
        if len(s.strip()) > 10
    ]
