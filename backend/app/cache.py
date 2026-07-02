"""Redis cache client with helper methods."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Global client instance ─────────────────────────────────────
_redis_client: Redis | None = None


async def get_redis() -> Redis:
    """Return (or create) the Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


async def check_redis_connection() -> bool:
    """Health check — verify Redis connectivity."""
    try:
        client = await get_redis()
        return await client.ping()
    except Exception:
        return False


# ── Cache helpers ──────────────────────────────────────────────

def make_cache_key(*parts: str) -> str:
    """Create a namespaced cache key."""
    raw = ":".join(parts)
    return f"medverify:{raw}"


def make_query_cache_key(question: str, model: str) -> str:
    """Create a SHA-256 cache key for a question + model pair."""
    content = f"{question.strip().lower()}:{model}"
    digest = hashlib.sha256(content.encode()).hexdigest()
    return make_cache_key("query", digest)


async def cache_get(key: str) -> Any | None:
    """Retrieve a cached JSON value."""
    try:
        client = await get_redis()
        value = await client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception as exc:
        logger.warning("cache_get_error", key=key, error=str(exc))
        return None


async def cache_set(
    key: str,
    value: Any,
    ttl: int = settings.CACHE_TTL_SECONDS,
) -> bool:
    """Store a JSON-serializable value in cache."""
    try:
        client = await get_redis()
        serialized = json.dumps(value, default=str)
        await client.setex(key, ttl, serialized)
        return True
    except Exception as exc:
        logger.warning("cache_set_error", key=key, error=str(exc))
        return False


async def cache_delete(key: str) -> bool:
    """Delete a cache entry."""
    try:
        client = await get_redis()
        result = await client.delete(key)
        return bool(result)
    except Exception as exc:
        logger.warning("cache_delete_error", key=key, error=str(exc))
        return False


async def cache_exists(key: str) -> bool:
    """Check if a key exists in cache."""
    try:
        client = await get_redis()
        return bool(await client.exists(key))
    except Exception:
        return False


# ── Rate limiting helpers ──────────────────────────────────────

async def rate_limit_check(
    user_id: str,
    endpoint: str,
    limit: int,
    window: int = settings.RATE_LIMIT_WINDOW_SECONDS,
) -> tuple[bool, int, int]:
    """
    Check rate limit for a user + endpoint.

    Returns:
        (allowed: bool, current_count: int, remaining: int)
    """
    key = make_cache_key("ratelimit", user_id, endpoint)
    try:
        client = await get_redis()
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        count = int(results[0])
        remaining = max(0, limit - count)
        return count <= limit, count, remaining
    except Exception as exc:
        logger.warning("rate_limit_error", user_id=user_id, error=str(exc))
        return True, 0, limit  # fail open
