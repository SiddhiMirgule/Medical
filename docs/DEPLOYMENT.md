# MedVerify AI — Production Deployment Guide

## Architecture Overview

```
Internet → Nginx (80) → Frontend (Next.js :3000)
                      → Backend (FastAPI :8000)
                            ├── PostgreSQL (RDS)
                            ├── Redis (ElastiCache)
                            ├── Qdrant (managed/self-hosted)
                            └── MinIO / S3 (document storage)
```

## Prerequisites

- Docker & Docker Compose (local/staging)
- AWS account (production) or equivalent cloud provider
- LLM API keys (OpenAI, Anthropic)
- NCBI API key (PubMed ingestion)

## Local Development

```bash
cp .env.example .env
# Edit .env with your API keys

docker compose up --build
```

Services:
| Service    | URL                    |
|------------|------------------------|
| Frontend   | http://localhost:3000  |
| Backend    | http://localhost:8000  |
| API Docs   | http://localhost:8000/docs |
| Nginx      | http://localhost:80    |
| Adminer    | http://localhost:8080 (dev profile) |

## Environment Variables

See `.env.example` for the complete list. Critical production variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | App secret (64+ chars) |
| `JWT_SECRET_KEY` | JWT signing key |
| `DATABASE_URL` | PostgreSQL async DSN |
| `REDIS_URL` | Redis connection string |
| `OPENAI_API_KEY` | GPT-4o access |
| `ANTHROPIC_API_KEY` | Claude access |
| `QDRANT_HOST` | Vector DB host |

## Database Migrations

```bash
cd backend
alembic upgrade head
```

## Data Ingestion

```bash
cd backend
python -m scripts.ingest --query "metformin diabetes" --source all
```

## Production Deployment (AWS)

### Recommended Stack

| Component | Service |
|-----------|---------|
| Frontend | Vercel or CloudFront + S3 |
| Backend | ECS Fargate |
| Database | RDS PostgreSQL 16 |
| Cache | ElastiCache Redis |
| Vector DB | Qdrant Cloud or self-hosted EC2 |
| Storage | S3 |
| Monitoring | Grafana Cloud + Prometheus |
| Tracing | OpenTelemetry Collector |

### Scaling Strategy

- **Backend**: Horizontal scaling via ECS task count (2-10 tasks)
- **Workers**: Celery workers for ingestion/evaluation (separate ECS service)
- **Qdrant**: Shard by collection; replicate for read scaling
- **Redis**: Cluster mode for rate limiting and caching
- **PostgreSQL**: Read replicas for analytics queries

### Backup Strategy

| Data | Method | Frequency |
|------|--------|-----------|
| PostgreSQL | RDS automated snapshots | Daily |
| Qdrant | Volume snapshots | Daily |
| S3/MinIO | Versioning + cross-region replication | Continuous |
| Redis | AOF persistence | Continuous |

### Disaster Recovery

1. **RPO**: 24 hours (daily snapshots)
2. **RTO**: 2 hours (automated failover + restore)
3. Restore PostgreSQL from latest RDS snapshot
4. Restore Qdrant from volume snapshot
5. Redeploy backend/frontend from container registry
6. Verify health endpoints and run smoke tests

## Monitoring

- Prometheus metrics at `/metrics`
- Health check at `/api/v1/health`
- Structured JSON logs via structlog
- OpenTelemetry traces (configure exporter in production)

## Security Checklist

- [ ] Rotate all secrets in production
- [ ] Enable HTTPS/TLS termination at load balancer
- [ ] Configure WAF rules
- [ ] Set restrictive CORS origins
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Use IAM roles (not access keys) for AWS services

## Smoke Tests

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/models
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the side effects of Metformin?"}'
```
