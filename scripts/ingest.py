#!/usr/bin/env python3
"""CLI script for document ingestion."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.pipeline import INGESTERS, run_full_ingestion, ingest_from_source


async def main() -> None:
    parser = argparse.ArgumentParser(description="MedVerify AI document ingestion")
    parser.add_argument("--query", default="metformin diabetes", help="Search query")
    parser.add_argument("--source", default="all", choices=["all", *INGESTERS.keys()])
    parser.add_argument("--max-results", type=int, default=100)
    args = parser.parse_args()

    if args.source == "all":
        result = await run_full_ingestion(args.query)
    else:
        result = await ingest_from_source(args.source, args.query, args.max_results)

    print(f"Ingestion complete: {result}")


if __name__ == "__main__":
    asyncio.run(main())
