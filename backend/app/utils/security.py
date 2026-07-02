"""JWT security utilities and password hashing."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.utils.exceptions import TokenExpiredError, TokenInvalidError

# ── Password hashing ──────────────────────────────────────────────────────────

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


# ── JWT token generation ──────────────────────────────────────────────────────

def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: User ID (UUID string) to embed as the 'sub' claim.
        extra_claims: Additional claims to include (e.g., role).

    Returns:
        Signed JWT string.
    """
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Create a signed JWT refresh token with a longer TTL.

    Args:
        subject: User ID (UUID string).

    Returns:
        Signed JWT string.
    """
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: Raw JWT string from Authorization header.

    Returns:
        Decoded payload dictionary.

    Raises:
        TokenExpiredError: If the token has expired.
        TokenInvalidError: If the token is malformed or signature is invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except JWTError as exc:
        raise TokenInvalidError() from exc


def decode_refresh_token(token: str) -> dict[str, Any]:
    """
    Decode a refresh token and validate its type claim.

    Raises:
        TokenInvalidError: If token type is not 'refresh'.
    """
    payload = decode_access_token(token)
    if payload.get("type") != "refresh":
        raise TokenInvalidError()
    return payload


# ── Utility helpers ───────────────────────────────────────────────────────────

def sha256_hex(text: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard the above",
    "you are now",
    "act as",
    "jailbreak",
    "dan mode",
    "developer mode",
    "pretend you are",
    "forget your instructions",
]


def detect_prompt_injection(text: str) -> bool:
    """
    Heuristic check for prompt injection attempts.

    Returns True if injection patterns are detected.
    """
    normalized = text.lower().strip()
    return any(pattern in normalized for pattern in INJECTION_PATTERNS)
