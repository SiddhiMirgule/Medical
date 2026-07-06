"""Authentication routes — register and login."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.dependencies import DBSession
from app.schemas import TokenResponse, UserCreate, UserLogin
from app.services import AuthService
from app.utils.audit import log_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, db: DBSession, request: Request) -> TokenResponse:
    service = AuthService(db)
    try:
        result = await service.register(body.email, body.password, body.role)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    await log_audit(
        db,
        action="user.register",
        user_id=result.user_id,
        resource_type="user",
        resource_id=str(result.user_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: DBSession, request: Request) -> TokenResponse:
    service = AuthService(db)
    try:
        result = await service.login(body.email, body.password)
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

    await log_audit(
        db,
        action="user.login",
        user_id=result.user_id,
        resource_type="user",
        resource_id=str(result.user_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )
