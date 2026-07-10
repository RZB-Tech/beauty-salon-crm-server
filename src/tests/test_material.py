import pytest
from src.tests.authContext import auth_client

pytestmark = pytest.mark.asyncio

async def test_2_create_salon_object(auth_client):
    """
    Step 2: Create a protected object.
    Because we are using the same 'auth_client', the authorization cookies 
    from test_1 are automatically sent with this request!
    """
    salon_payload = {
        "article": "MT-ASAD",
        "name": "SOME NAME"
    }
    
    response = await auth_client.post("/api/v1/materials", json=salon_payload)
    
    assert response.status_code == 201