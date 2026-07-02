MedVerify AI

Evidence-Grounded Medical Question Answering, Claim Verification, and Hallucination Detection Platform

MedVerify AI is a research-grade medical AI system that answers healthcare questions using trusted medical literature and provides claim-level verification, hallucination detection, confidence scoring, explainability, and evaluation metrics.

The platform demonstrates advanced techniques in:

Retrieval-Augmented Generation (RAG)
AI Safety
Explainable AI (XAI)
Medical Knowledge Retrieval
Hallucination Detection
LLM Evaluation
Benchmarking & Model Comparison
Overview

Large Language Models can generate plausible but incorrect medical information. MedVerify AI addresses this challenge by grounding responses in trusted medical sources and verifying every generated claim against retrieved evidence.

Core Workflow
User Question
      │
      ▼
Hybrid Retrieval
(BM25 + Dense Search)
      │
      ▼
Reranking
      │
      ▼
Answer Generation
      │
      ▼
Claim Extraction
      │
      ▼
Evidence Verification
      │
      ▼
Hallucination Detection
      │
      ▼
Confidence Scoring
      │
      ▼
Explainability Layer
      │
      ▼
Final Verified Response
Key Features
Evidence-Based Medical Question Answering

Generate answers strictly from retrieved medical literature.

Example

Question

What are the side effects of Metformin?

Output

Metformin is commonly associated with gastrointestinal side effects,
including nausea, diarrhea, abdominal discomfort, and loss of appetite.

Source:
PubMed PMID: XXXXXXX
Publication Date: YYYY-MM-DD
Safety Rules
No unsupported claims
No fabricated information
Evidence-backed responses only
Explicit handling of uncertainty

If evidence is insufficient:

Insufficient evidence found.
Claim Extraction

Every generated answer is decomposed into atomic factual claims.

Example

Input:

Metformin lowers blood glucose and may cause nausea.

Output:

[
  {
    "claim": "Metformin lowers blood glucose"
  },
  {
    "claim": "Metformin may cause nausea"
  }
]
Evidence Verification

Each claim is verified against retrieved literature.

Verification Categories:

Supported
Partially Supported
Unsupported
Contradicted

Example:

{
  "claim": "Metformin may cause nausea",
  "status": "Supported",
  "confidence": 0.94,
  "evidence": [
    {
      "source": "PubMed",
      "excerpt": "The most common adverse effect is nausea..."
    }
  ]
}
Hallucination Detection

Claims are evaluated for factual grounding.

Classification:

Verified
Low Confidence
Potential Hallucination

Example:

Overall Hallucination Risk: 12%

Claims:
✓ Verified
✓ Verified
⚠ Potential Hallucination
Confidence Scoring

Confidence is computed using multiple signals:

Retriever similarity score
Number of supporting sources
Cross-source agreement
Verifier model confidence
Entailment score

Formula is configurable through the admin panel.

Explainability Dashboard

Every answer includes transparent reasoning.

Displayed Information:

Claim
Verification status
Confidence score
Supporting evidence
Publication details
Source metadata

Users can inspect why the system produced a specific answer.

Source Explorer

Explore retrieved medical literature.

Available Metadata:

Title
Authors
Publication Date
PMID
Abstract
Source URL
Citation Information
RAG Evaluation Dashboard

Evaluate retrieval and generation quality.

Metrics:

Faithfulness
Context Precision
Context Recall
Answer Relevancy

Powered by:

RAGAS
DeepEval
Benchmark Mode

Compare multiple LLMs on medical QA tasks.

Supported Models:

GPT-4o
Claude Sonnet
Llama 3.1

Metrics:

Accuracy
Hallucination Rate
Faithfulness
Latency
Cost

Includes leaderboard and historical comparisons.

Research Mode

Provides full transparency into the RAG pipeline.

Displays:

Retrieved papers
Retrieved chunks
Embedding similarity scores
Reranking results
Verification evidence
Hallucination analysis

Designed for researchers and evaluators.

Technology Stack
Frontend
Technology	Purpose
Next.js 15	Application Framework
TypeScript	Type Safety
TailwindCSS	Styling
Shadcn UI	Component Library
TanStack Query	Data Fetching
Zustand	State Management
Recharts	Analytics & Charts
Backend
Technology	Purpose
FastAPI	API Layer
Python 3.12	Core Language
Pydantic v2	Validation
SQLAlchemy	ORM
Redis	Cache & Queue
Celery	Background Tasks
AI Stack
Technology	Purpose
LangGraph	Agent Workflow
LangChain	LLM Orchestration
LlamaIndex	Retrieval Layer
Retrieval Stack
Technology	Purpose
Qdrant	Vector Database
BM25	Sparse Retrieval
BGE Large	Embeddings
BGE Reranker	Context Reranking
LLM Providers
Model	Usage
GPT-4o	Answer Generation
Claude Sonnet	Verification
Llama 3.1	Benchmarking
Evaluation
Framework	Purpose
RAGAS	RAG Evaluation
DeepEval	Hallucination Analysis
Storage
Technology	Purpose
PostgreSQL	Relational Data
Redis	Caching
S3 / MinIO	Document Storage
Data Sources

MedVerify AI ingests trusted medical literature from:

PubMed
National Institutes of Health
World Health Organization
Clinical Practice Guidelines
Government Health Resources
Peer-Reviewed Publications
System Architecture
                        ┌─────────────────┐
                        │     Frontend     │
                        │    Next.js 15    │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │     FastAPI      │
                        └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼

 ┌─────────────┐       ┌────────────────┐      ┌─────────────┐
 │ PostgreSQL │       │     Redis       │      │     S3      │
 └─────────────┘       └────────────────┘      └─────────────┘

                                 │
                                 ▼

                      ┌────────────────────┐
                      │     LangGraph      │
                      └─────────┬──────────┘
                                │
                                ▼

                   ┌─────────────────────────┐
                   │ Hybrid Retrieval Engine │
                   └─────────┬───────────────┘
                             │
                             ▼

                      ┌─────────────┐
                      │   Qdrant    │
                      └─────────────┘

                             │
                             ▼

                    ┌─────────────────┐
                    │ Medical Sources │
                    └─────────────────┘
Project Structure
medverify-ai/

├── frontend/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── lib/
│   └── types/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   ├── models/
│   └── workers/
│
├── ai/
│   ├── graph/
│   ├── retrieval/
│   ├── verification/
│   ├── hallucination/
│   ├── prompts/
│   └── evaluation/
│
├── ingestion/
│   ├── pubmed/
│   ├── nih/
│   ├── who/
│   └── guidelines/
│
├── benchmark/
│
├── tests/
│
├── docker/
│
├── docs/
│
└── scripts/
API Endpoints
Question Answering
POST /ask

Generate evidence-backed medical answers.

Claim Extraction
POST /extract-claims

Extract atomic claims from generated responses.

Verification
POST /verify

Verify claims against retrieved evidence.

Evaluation
POST /evaluate

Run RAGAS and DeepEval evaluations.

Sources
GET /sources

Retrieve source documents.

Metrics
GET /metrics

Retrieve evaluation metrics.

Benchmark
GET /benchmark

Retrieve model comparison results.

Deployment
Local Development
docker compose up --build

Services:

Frontend
Backend
PostgreSQL
Redis
Qdrant
MinIO
Production

Recommended Infrastructure:

Frontend: Vercel
Backend: AWS ECS/Fargate
Database: PostgreSQL (RDS)
Cache: Redis Cloud
Storage: S3
Monitoring: Grafana
Tracing: OpenTelemetry
Testing
Unit Tests
pytest tests/unit
Integration Tests
pytest tests/integration
Coverage
pytest --cov
Research Contributions

This project explores:

Medical RAG Systems
Hallucination Detection
Explainable AI
LLM Verification
Retrieval Evaluation
Evidence-Grounded Generation
AI Safety in Healthcare
Disclaimer

MedVerify AI is intended for research, educational, and evaluation purposes.

The system is not a medical device and should not be used as a substitute for professional medical advice, diagnosis, or treatment.

Always consult qualified healthcare professionals for medical decisions.

License

MIT License

Future Roadmap
Multi-modal medical retrieval
Medical image support
Clinical trial integration
Real-time guideline updates
Federated medical knowledge indexing
Citation graph analysis
Automated evidence synthesis
Multi-agent medical review workflows

MedVerify AI — Building Trustworthy, Explainable, and Evidence-Grounded Medical AI.
