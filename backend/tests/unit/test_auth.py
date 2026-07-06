"""Unit tests for authentication service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services import AuthService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)


class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_rejects_duplicate_email(self, auth_service):
        auth_service.user_repo.get_by_email = AsyncMock(return_value=MagicMock())
        with pytest.raises(ValueError, match="already registered"):
            await auth_service.register("test@example.com", "password123")

    @pytest.mark.asyncio
    async def test_login_rejects_invalid_credentials(self, auth_service):
        auth_service.user_repo.get_by_email = AsyncMock(return_value=None)
        with pytest.raises(ValueError, match="Invalid email"):
            await auth_service.login("test@example.com", "wrong")

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service):
        auth_service.user_repo.get_by_email = AsyncMock(return_value=None)
        user = MagicMock()
        user.id = uuid4()
        user.role = "user"
        auth_service.user_repo.create = AsyncMock(return_value=user)

        result = await auth_service.register("new@example.com", "securepass123")
        assert result.access_token
        assert result.refresh_token
        assert result.user_id == user.id
