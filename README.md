medverify-ai/
├── frontend/                          # Next.js 15 App Router
│   ├── app/
│   │   ├── (public)/                  # landing, about
│   │   ├── (app)/                     # authenticated app shell
│   │   │   ├── ask/
│   │   │   ├── results/[queryId]/
│   │   │   ├── explain/[queryId]/
│   │   │   ├── sources/
│   │   │   ├── research/[queryId]/
│   │   │   └── admin/
│   │   │       ├── evaluation/
│   │   │       ├── benchmark/
│   │   │       └── settings/
│   │   ├── api/                       # optional BFF proxies
│   │   └── layout.tsx
│   ├── components/ui/                 # shadcn
│   ├── features/
│   │   ├── ask/
│   │   ├── explainability/
│   │   ├── sources/
│   │   ├── evaluation/
│   │   ├── benchmark/
│   │   └── research/
│   ├── hooks/
│   ├── lib/api-client.ts
│   ├── stores/                        # Zustand
│   └── types/
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   ├── ask.py
│   │   │   ├── verify.py
│   │   │   ├── claims.py
│   │   │   ├── evaluate.py
│   │   │   ├── benchmark.py
│   │   │   ├── sources.py
│   │   │   ├── metrics.py
│   │   │   ├── models.py
│   │   │   ├── health.py
│   │   │   └── auth.py
│   │   ├── core/
│   │   │   ├── middleware.py
│   │   │   ├── rate_limit.py
│   │   │   └── telemetry.py
│   │   ├── models/                    # SQLAlchemy (extend existing)
│   │   ├── schemas/                   # Pydantic v2 DTOs
│   │   ├── repositories/
│   │   ├── services/
│   │   └── workers/                   # Celery tasks
│   ├── ai/
│   │   ├── graph/
│   │   │   ├── state.py
│   │   │   ├── nodes/
│   │   │   └── medverify_graph.py
│   │   ├── retrieval/
│   │   │   ├── dense.py
│   │   │   ├── sparse.py
│   │   │   ├── fusion.py
│   │   │   └── reranker.py
│   │   ├── generation/
│   │   ├── verification/
│   │   ├── hallucination/
│   │   ├── confidence/
│   │   ├── llm/
│   │   │   └── factory.py             # provider abstraction
│   │   └── prompts/
│   ├── ingestion/
│   │   ├── base.py
│   │   ├── pubmed/
│   │   ├── nih/
│   │   ├── who/
│   │   └── guidelines/
│   ├── alembic/versions/
│   └── tests/
│
├── benchmark/datasets/
├── docs/
├── scripts/
├── .github/workflows/
└── docker-compose.yml

SYSTEM ARCHITECTURE 
flowchart TB
    subgraph Client
        FE[Next.js 15 Frontend]
    end

    subgraph API
        GW[Nginx]
        API[FastAPI]
    end

    subgraph Orchestration
        LG[LangGraph Workflow]
        LLM[LLM Factory<br/>GPT-4o / Claude / Llama]
    end

    subgraph Retrieval
        HY[Hybrid Retriever]
        BM25[BM25 / Postgres FTS]
        DENSE[BGE + Qdrant]
        RRF[RRF Fusion]
        RERANK[BGE Reranker]
    end

    subgraph Storage
        PG[(PostgreSQL)]
        RD[(Redis)]
        QD[(Qdrant)]
        S3[(MinIO/S3)]
    end

    subgraph Workers
        CEL[Celery Workers]
        ING[Ingestion Pipelines]
    end

    FE --> GW --> API
    API --> LG
    LG --> HY --> RRF --> RERANK
    HY --> BM25
    HY --> DENSE
    LG --> LLM
    API --> PG
    API --> RD
    DENSE --> QD
    ING --> S3
    ING --> PG
    ING --> QD
    CEL --> ING
