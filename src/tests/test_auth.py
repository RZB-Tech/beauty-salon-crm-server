import pytest
from httpx import ASGITransport, AsyncClient
from src.app import app 

pytestmark = pytest.mark.asyncio(loop_scope="session")

async def test_login_refresh_logout_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://testserver") as client:
        
        # --- 1. LOGIN ---
        payload = {
            "login": "admin",
            "password": "test"
        }
        response = await client.post("/api/v1/auth/login", json=payload)
        
        assert response.status_code == 200
        assert "access_token" in client.cookies
        assert "refresh_token" in client.cookies

        # --- 2. REFRESH ---
        refresh_response = await client.post("/api/v1/auth/refresh")
        
        assert refresh_response.status_code == 204

        # LOGOUT
        logoutResponse = await client.post("/api/v1/auth/logout")
        assert logoutResponse.status_code == 204