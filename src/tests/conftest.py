import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from src.app import app

@pytest_asyncio.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://testserver") as c:
        yield c

@pytest_asyncio.fixture(scope="session")
async def auth_client(client):
    """Logs in once, then hands back the same client with cookies already set."""
    payload = {"login": "admin", "password": "test"}
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    return client