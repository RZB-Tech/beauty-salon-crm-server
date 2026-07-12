import pytest
pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestClient:

    clientID: int

    async def test_client_create(self, auth_client):
        salon_payload = {
            "firstname": "SOME NAME",
            "sex": "male",
        }
        response = await auth_client.post("/api/v1/clients", json=salon_payload)
        TestClient.clientID = int(response.json()["id"])
        assert response.status_code == 201

    async def test_client_create_with_deposit(self, auth_client):
        salon_payload = {
            "firstname": "SOME Name 2",
            "sex": "male",
            "deposit": 100
        }
        response = await auth_client.post("/api/v1/clients", json=salon_payload)
        assert response.status_code == 201
        assert response.json()["deposit"] == 100

    async def test_client_get(self, auth_client):
        response = await auth_client.get(f"/api/v1/clients/{TestClient.clientID}")
        assert response.status_code == 200

    async def test_client_get_not_found(self, auth_client):
        response = await auth_client.get(f"/api/v1/clients/99999")
        assert response.status_code == 404

    async def test_client_patch(self, auth_client):
        patch_payload = {
            "id": TestClient.clientID,
            "firstname": "UPDATED NAME"
        }
        response = await auth_client.patch(f"/api/v1/clients", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["firstname"] == "UPDATED NAME"

    async def test_client_update_deposit(self, auth_client):
        patch_payload = {
            "id": TestClient.clientID,
            "operation": 1,
            "amount": 200
        }
        response = await auth_client.post(f"/api/v1/clients/update-deposit", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["deposit"] == 200

    async def test_client_update_deposit_negative(self, auth_client):
        patch_payload = {
            "id": TestClient.clientID,
            "operation": -1,
            "amount": 100
        }
        response = await auth_client.post(f"/api/v1/clients/update-deposit", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["deposit"] == 100

    async def test_client_update_deposit_negative_not_enough(self, auth_client):
        patch_payload = {
            "id": TestClient.clientID,
            "operation": -1,
            "amount": 200
        }
        response = await auth_client.post(f"/api/v1/clients/update-deposit", json=patch_payload)
        assert response.status_code == 409

    async def test_client_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/clients/get-all", json={})
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_client_patch_set_archived(self, auth_client):
        patch_payload = {
            "id": TestClient.clientID,
            "archived": True
        }
        response = await auth_client.patch(f"/api/v1/clients", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["archived"] == True