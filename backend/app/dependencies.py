"""FastAPI dependency injection providers."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.config import Settings, get_settings
from app.database import get_db
from app.utils.exceptions import AuthenticationError, RateLimitError
from app.utils.logger import get_logger
from app.utils.security import decode_access_token

logger = get_logger(__name__)

# ── Type aliases for DI ────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]

# ── Bearer token extractor ─────────────────────────────────────
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> UUID:
    """
    Validate JWT Bearer token and return the authenticated user's ID.
    Raises HTTP 401 if token is missing or invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Token missing subject claim")
        return UUID(user_id_str)
    except (AuthenticationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_optional_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> UUID | None:
    """Like get_current_user_id but returns None if no token provided."""
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id_str = payload.get("sub")
        return UUID(user_id_str) if user_id_str else None
    except Exception:
        return None


async def require_admin(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: DBSession,
) -> UUID:
    """
    Validate that the current user has the 'admin' role.
    Raises HTTP 403 if not.
    """
    from app.repositories import UserRepository

    repo = UserRepository(db)
    user = await repo.get_by_id(current_user_id)
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )
    return current_user_id


async def get_request_id(request: Request) -> str:
    """Extract the request ID set by middleware."""
    return getattr(request.state, "request_id", "unknown")


# ── Convenient dependency type aliases ─────────────────────────
CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
OptionalUser = Annotated[UUID | None, Depends(get_optional_user_id)]
AdminUser = Annotated[UUID, Depends(require_admin)]
RequestId = Annotated[str, Depends(get_request_id)]
