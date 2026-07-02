"""Custom exception hierarchy for MedVerify AI."""

from __future__ import annotations

from http import HTTPStatus


class MedVerifyError(Exception):
    """Base exception for all application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str = "An unexpected error occurred") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r})"


# ── Authentication & Authorization ───────────────────────────────────────────

class AuthenticationError(MedVerifyError):
    """Raised when authentication fails."""
    status_code = 401
    error_code = "UNAUTHORIZED"


class AuthorizationError(MedVerifyError):
    """Raised when user lacks required permissions."""
    status_code = 403
    error_code = "FORBIDDEN"


class TokenExpiredError(AuthenticationError):
    """Raised when a JWT token has expired."""
    error_code = "TOKEN_EXPIRED"

    def __init__(self) -> None:
        super().__init__("Authentication token has expired")


class TokenInvalidError(AuthenticationError):
    """Raised when a JWT token is malformed or invalid."""
    error_code = "TOKEN_INVALID"

    def __init__(self) -> None:
        super().__init__("Authentication token is invalid")


# ── Resource Errors ───────────────────────────────────────────────────────────

class NotFoundError(MedVerifyError):
    """Raised when a requested resource does not exist."""
    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, resource: str, identifier: str | None = None) -> None:
        msg = f"{resource} not found"
        if identifier:
            msg = f"{resource} '{identifier}' not found"
        super().__init__(msg)
        self.resource = resource
        self.identifier = identifier


class ConflictError(MedVerifyError):
    """Raised when a resource conflict occurs (e.g., duplicate email)."""
    status_code = 409
    error_code = "CONFLICT"


class ValidationError(MedVerifyError):
    """Raised when input validation fails at the service layer."""
    status_code = 422
    error_code = "VALIDATION_ERROR"


# ── AI / Medical Domain Errors ────────────────────────────────────────────────

class InsufficientEvidenceError(MedVerifyError):
    """Raised when retrieved evidence is insufficient to answer the question."""
    status_code = 422
    error_code = "INSUFFICIENT_EVIDENCE"

    def __init__(self, question: str | None = None) -> None:
        msg = "Insufficient medical evidence found to answer this question reliably."
        if question:
            msg = f"Insufficient evidence to answer: '{question[:100]}...'"
        super().__init__(msg)


class LLMUnavailableError(MedVerifyError):
    """Raised when the LLM provider is unavailable."""
    status_code = 503
    error_code = "LLM_UNAVAILABLE"

    def __init__(self, provider: str = "LLM") -> None:
        super().__init__(f"{provider} provider is currently unavailable. Please try again later.")


class EmbeddingError(MedVerifyError):
    """Raised when embedding generation fails."""
    status_code = 500
    error_code = "EMBEDDING_ERROR"


class RetrievalError(MedVerifyError):
    """Raised when vector retrieval fails."""
    status_code = 500
    error_code = "RETRIEVAL_ERROR"


class IngestionError(MedVerifyError):
    """Raised when document ingestion fails."""
    status_code = 500
    error_code = "INGESTION_ERROR"


class PromptInjectionError(MedVerifyError):
    """Raised when a potential prompt injection attempt is detected."""
    status_code = 400
    error_code = "PROMPT_INJECTION_DETECTED"

    def __init__(self) -> None:
        super().__init__(
            "Your input contains patterns that could compromise system safety. "
            "Please rephrase your medical question."
        )


# ── Infrastructure Errors ──────────────────────────────────────────────────────

class RateLimitError(MedVerifyError):
    """Raised when a user exceeds rate limits."""
    status_code = 429
    error_code = "RATE_LIMITED"

    def __init__(self, limit: int, window: int) -> None:
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window} seconds. "
            "Please wait before retrying."
        )
        self.limit = limit
        self.window = window


class CacheError(MedVerifyError):
    """Raised when Redis cache operations fail."""
    status_code = 500
    error_code = "CACHE_ERROR"


class DatabaseError(MedVerifyError):
    """Raised when database operations fail."""
    status_code = 500
    error_code = "DATABASE_ERROR"


class ExternalServiceError(MedVerifyError):
    """Raised when an external API call fails."""
    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"

    def __init__(self, service: str, detail: str = "") -> None:
        msg = f"External service '{service}' failed"
        if detail:
            msg = f"{msg}: {detail}"
        super().__init__(msg)
        self.service = service
