import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestServiceCategory:
    serviceCategoryID: int

    async def test_serviceCategory_create(self, auth_client):
        salon_payload = {
            "name": "SOME NAME"
        }
        response = await auth_client.post("/api/v1/service-categories", json=salon_payload)
        TestServiceCategory.serviceCategoryID = int(response.json()["id"])
        assert response.status_code == 201

    async def test_serviceCategory_duplicate_name(self, auth_client):
        salon_payload = {
            "name": "SOME NAME"
        }
        response = await auth_client.post("/api/v1/service-categories", json=salon_payload)
        assert response.status_code == 409

    async def test_serviceCategory_get(self,auth_client):
        response = await auth_client.get(f"/api/v1/service-categories/{TestServiceCategory.serviceCategoryID}")
        assert response.status_code == 200
        assert response.json()["name"] == "SOME NAME"

    async def test_serviceCategory_get_not_found(self, auth_client):
        response = await auth_client.get("/api/v1/service-categories/9999")
        assert response.status_code == 404

    async def test_serviceCategory_patch(self, auth_client):
        patch_payload = {
            "id": TestServiceCategory.serviceCategoryID,
            "name": "NEW NAME"
        }
        response = await auth_client.patch("/api/v1/service-categories", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["name"] == "NEW NAME"

    async def test_serviceCategory_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/service-categories/get-all", json={})
        print(response.json())
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_serviceCategory_patch_set_archived(self, auth_client):
        patch_payload = {
            "id": 1,
            "archived": True
        }
        response = await auth_client.patch("/api/v1/service-categories", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["archived"] == True