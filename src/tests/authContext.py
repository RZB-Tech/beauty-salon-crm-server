from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from src.app import app

@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def auth_client():
    """
    Creates an authenticated HTTP client for protected endpoint tests.
    The login request stores access_token and refresh_token cookies
    inside the same AsyncClient instance.
    """
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="https://testserver",
    ) as client:
        login_payload = {
            "login": "admin",
            "password": "test",
        }

        login_response = await client.post("/api/v1/auth/login", json=login_payload)

        assert login_response.status_code == 200
        assert "access_token" in client.cookies
        assert "refresh_token" in client.cookies

        yield client