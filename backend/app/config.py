"""Application configuration using Pydantic Settings v2."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration — all values loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────
    APP_NAME: str = "MedVerify AI"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = Field(min_length=32)
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    API_V1_PREFIX: str = "/api/v1"

    # ── JWT ─────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── PostgreSQL ──────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "medverify"
    POSTGRES_USER: str = "medverify_user"
    POSTGRES_PASSWORD: str
    DATABASE_URL: str  # asyncpg DSN
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # ── Redis ───────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: str
    CACHE_TTL_SECONDS: int = 3600
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Qdrant ──────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "medical_documents"
    QDRANT_VECTOR_SIZE: int = 1024

    # ── LLM Providers ───────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_DEFAULT_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.1

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_DEFAULT_MODEL: str = "claude-sonnet-4-5"
    ANTHROPIC_MAX_TOKENS: int = 4096

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.1"

    DEFAULT_LLM_MODEL: Literal["gpt-4o", "claude-sonnet", "llama-3.1"] = "gpt-4o"

    # ── Embeddings ──────────────────────────────────────────────
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cpu"

    # ── Ingestion ───────────────────────────────────────────────
    NCBI_API_KEY: str = ""
    PUBMED_MAX_RESULTS: int = 1000
    INGESTION_CHUNK_SIZE: int = 512
    INGESTION_CHUNK_OVERLAP: int = 64

    # ── Rate Limiting ───────────────────────────────────────────
    RATE_LIMIT_ASK: int = 30
    RATE_LIMIT_VERIFY: int = 60
    RATE_LIMIT_DEFAULT: int = 100

    # ── CORS ────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # ── Observability ───────────────────────────────────────────
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "medverify-dev"
    LANGSMITH_TRACING: bool = False
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    # ── Evaluation ──────────────────────────────────────────────
    RAGAS_BATCH_SIZE: int = 5
    DEEPEVAL_API_KEY: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str | None, info: Any) -> str:
        if v:
            return v
        data = info.data
        return (
            f"postgresql+asyncpg://{data['POSTGRES_USER']}:{data['POSTGRES_PASSWORD']}"
            f"@{data['POSTGRES_HOST']}:{data['POSTGRES_PORT']}/{data['POSTGRES_DB']}"
        )

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: str | None, info: Any) -> str:
        if v:
            return v
        data = info.data
        password_part = f":{data['REDIS_PASSWORD']}@" if data.get("REDIS_PASSWORD") else ""
        return f"redis://{password_part}{data['REDIS_HOST']}:{data['REDIS_PORT']}/{data['REDIS_DB']}"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
