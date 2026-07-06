# MedVerify AI

> Evidence-Grounded Medical Question Answering, Claim Verification, and Hallucination Detection Platform

MedVerify AI is a research-grade AI platform designed to answer medical questions using trusted medical literature while providing transparent claim verification, hallucination detection, confidence scoring, explainability, and evaluation metrics.

The system combines Retrieval-Augmented Generation (RAG), AI Safety, Explainable AI (XAI), LLM Evaluation, and Multi-Model Benchmarking to produce trustworthy, auditable, and evidence-backed responses.

---

## Mission

Large Language Models can generate convincing but inaccurate medical information.

MedVerify AI addresses this problem by:

* Retrieving information from trusted medical sources
* Grounding responses in scientific evidence
* Verifying every generated claim
* Detecting hallucinations
* Providing explainable reasoning
* Measuring answer quality using industry-standard evaluation frameworks

---

## Core Features

### Medical Question Answering

Generate evidence-grounded responses using trusted medical literature.

**Example Query**

```text
What are the side effects of Metformin?
```

**System Behavior**

* Retrieves relevant medical literature
* Generates answers only from retrieved evidence
* Includes source citations
* Provides confidence scores
* Refuses unsupported conclusions

If evidence is insufficient:

```text
Insufficient evidence found.
```
```
---

### Hallucination Detection

Every answer undergoes hallucination analysis.

Classifications:

* Verified
* Low Confidence
* Hallucinated

Example:

```text
Overall Hallucination Risk: 12%
```

---

### Confidence Scoring

Confidence is computed using:

* Retrieval similarity
* Supporting evidence count
* Source agreement
* Verifier confidence
* Entailment scores

Outputs:

* Overall confidence
* Claim-level confidence

---

### Explainability Dashboard

Users can inspect:

* Claims
* Supporting evidence
* Confidence scores
* Verification status
* Source publications
* Similarity scores

This enables complete transparency into system decisions.

---

### RAG Evaluation Dashboard

Evaluate system quality using:

#### RAGAS

* Faithfulness
* Context Precision
* Context Recall
* Answer Relevancy

#### DeepEval

* Hallucination Rate
* Answer Quality
* Consistency

---

### Benchmark Mode

Compare multiple LLMs on medical QA tasks.

Supported models:

* GPT-4o
* Claude Sonnet
* Llama 3.1

Comparison metrics:

* Accuracy
* Hallucination Rate
* Faithfulness
* Cost
* Latency

---

### Research Mode

Provides full visibility into the RAG pipeline.

Displays:

* Retrieved papers
* Retrieved chunks
* Embedding similarities
* Reranking scores
* Verification results
* Hallucination analysis

Designed for researchers and evaluators.

---

# Architecture

```text
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
Final Response
```

---

# Technology Stack

## Frontend

* Next.js 15
* TypeScript
* TailwindCSS
* Shadcn UI
* TanStack Query
* Zustand
* Recharts

---

## Backend

* FastAPI
* Python 3.12
* SQLAlchemy
* Alembic
* Pydantic v2

---

## AI Stack

* LangGraph
* LangChain
* LlamaIndex

---

## Retrieval

* Qdrant
* BM25
* BAAI/bge-large-en-v1.5
* BAAI/bge-reranker-large

---

## LLM Providers

* OpenAI GPT-4o
* Claude Sonnet
* Llama 3.1

---

## Evaluation

* RAGAS
* DeepEval

---

## Storage

* PostgreSQL
* Redis
* MinIO / AWS S3
* 
---

# Data Sources

The system ingests trusted medical literature from:

* PubMed
* NIH Resources
* WHO Guidelines
* Clinical Practice Guidelines
* Government Health Publications
* Peer-Reviewed Medical Research

---

# Project Structure

```bash
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
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── workers/
│
├── ai/
│   ├── graph/
│   ├── retrieval/
│   ├── verification/
│   ├── hallucination/
│   ├── evaluation/
│   └── prompts/
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
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docker/
│
├── docs/
│
└── scripts/
```
```
```
---

# Evaluation Framework

Metrics tracked:

| Metric             | Description                     |
| ------------------ | ------------------------------- |
| Faithfulness       | Grounding in retrieved evidence |
| Context Precision  | Retrieval quality               |
| Context Recall     | Coverage of relevant evidence   |
| Answer Relevancy   | Question-answer alignment       |
| Hallucination Rate | Unsupported claims              |
| Latency            | Response speed                  |
| Cost               | Model inference cost            |

---

# Deployment

### Frontend

* Vercel

### Backend

* AWS ECS / Fargate

### Database

* PostgreSQL (RDS)

### Cache

* Redis Cloud

### Storage

* AWS S3

### Monitoring

* Grafana
* OpenTelemetry

---

# Security

Implemented security controls:

* JWT Authentication
* Role-Based Access Control (RBAC)
* Rate Limiting
* Input Validation
* Audit Logging
* Secrets Management
* Secure API Access

---

# Research Applications

MedVerify AI demonstrates:

* Retrieval-Augmented Generation (RAG)
* AI Safety Engineering
* Hallucination Detection
* Explainable AI
* Medical AI Systems
* LLM Evaluation
* Agentic Workflows
* Evidence-Based Reasoning

---

# Disclaimer

MedVerify AI is intended for research, educational, and evaluation purposes only.

This system is not a medical device and should not be used as a substitute for professional medical advice, diagnosis, or treatment.

Always consult qualified healthcare professionals for medical decisions.

---

Built to advance trustworthy, explainable, and evidence-grounded AI systems for healthcare.
<img width="842" height="1038" alt="image" src="https://github.com/user-attachments/assets/d26cad21-9b24-46ed-b38a-0fceee93d9f1" />
