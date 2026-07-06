#!/usr/bin/env python3
"""Seed demo medical documents into PostgreSQL for development."""

from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import AsyncSessionLocal
from app.repositories import DocumentRepository

DEMO_DOCUMENTS = [
    {
        "title": "Metformin in the Treatment of Type 2 Diabetes: A Systematic Review",
        "authors": ["Smith, J.", "Johnson, A.", "Williams, R."],
        "source": "PubMed",
        "publication_date": datetime(2024, 3, 15, tzinfo=UTC),
        "pmid": "38123456",
        "url": "https://pubmed.ncbi.nlm.nih.gov/38123456",
        "abstract": (
            "Metformin remains the first-line pharmacological treatment for type 2 diabetes mellitus. "
            "This systematic review examines its efficacy, safety profile, and common adverse effects "
            "including gastrointestinal symptoms such as nausea, diarrhea, and abdominal discomfort."
        ),
        "document_type": "journal_article",
        "keywords": ["metformin", "diabetes", "biguanide"],
    },
    {
        "title": "NIH Clinical Guidelines: Pharmacologic Approaches to Glycemic Treatment",
        "authors": ["National Institutes of Health"],
        "source": "NIH",
        "publication_date": datetime(2023, 11, 20, tzinfo=UTC),
        "pmid": "37890123",
        "url": "https://www.nih.gov/guidelines/diabetes",
        "abstract": (
            "Clinical practice guidelines recommend metformin as initial therapy for type 2 diabetes "
            "when lifestyle modifications are insufficient."
        ),
        "document_type": "health_resource",
        "keywords": ["metformin", "guidelines", "glycemic"],
    },
    {
        "title": "WHO Model List of Essential Medicines: Antidiabetic Agents",
        "authors": ["World Health Organization"],
        "source": "WHO",
        "publication_date": datetime(2024, 1, 10, tzinfo=UTC),
        "pmid": "37234567",
        "url": "https://www.who.int/medicines",
        "abstract": (
            "Metformin is included in the WHO Model List of Essential Medicines for the management "
            "of type 2 diabetes."
        ),
        "document_type": "guideline",
        "keywords": ["metformin", "essential medicines"],
    },
    {
        "title": "Lactic Acidosis Risk with Metformin: A Meta-Analysis",
        "authors": ["Chen, L.", "Patel, S."],
        "source": "PubMed",
        "publication_date": datetime(2023, 8, 5, tzinfo=UTC),
        "pmid": "36567890",
        "url": "https://pubmed.ncbi.nlm.nih.gov/36567890",
        "abstract": (
            "While metformin-associated lactic acidosis is rare, gastrointestinal side effects "
            "remain the most commonly reported adverse events."
        ),
        "document_type": "journal_article",
        "keywords": ["metformin", "lactic acidosis", "safety"],
    },
    {
        "title": "ADA Standards of Care in Diabetes—2024",
        "authors": ["American Diabetes Association"],
        "source": "Clinical Practice Guidelines",
        "publication_date": datetime(2024, 1, 1, tzinfo=UTC),
        "pmid": "38012345",
        "url": "https://diabetesjournals.org/care",
        "abstract": (
            "The American Diabetes Association recommends individualized glycemic targets "
            "and metformin as foundational therapy."
        ),
        "document_type": "guideline",
        "keywords": ["diabetes", "metformin", "standards of care"],
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)
        created = 0
        for doc_data in DEMO_DOCUMENTS:
            existing = await repo.get_by_pmid(doc_data["pmid"])
            if existing:
                continue
            await repo.create(id=uuid.uuid4(), indexed_at=datetime.now(UTC), **doc_data)
            created += 1
        await session.commit()
        print(f"Seeded {created} documents ({len(DEMO_DOCUMENTS) - created} already existed)")


if __name__ == "__main__":
    asyncio.run(seed())
