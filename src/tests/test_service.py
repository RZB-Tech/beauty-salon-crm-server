import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestService:
    serviceCategoryID: int
    serviceID: int

    async def test_service_create(self, auth_client):
        salon_payload = {
            "name": "SOME NAME"
        }
        response = await auth_client.post("/api/v1/services", json=salon_payload)
        TestService.serviceID = int(response.json()["id"])
        assert response.status_code == 201

    async def test_service_duplicate_name(self, auth_client):
        salon_payload = {
            "name": "SOME NAME"
        }
        response = await auth_client.post("/api/v1/services", json=salon_payload)
        assert response.status_code == 409

    async def test_service_create_with_price(self, auth_client):
        salon_payload = {
            "name": "SOME Name 2",
            "price": 100
        }
        response = await auth_client.post("/api/v1/services", json=salon_payload)
        assert response.status_code == 201
        assert response.json()["price"] == 100

    async def test_service_create_with_category(self, auth_client):
        serviceCategory = await auth_client.post("/api/v1/service-categories", json={"name": "for service test"})
        serviceCategoryID = serviceCategory.json()["id"]
        salon_payload = {
            "name": "SOME Name 3",
            "price": 100,
            "category_id": int(serviceCategoryID)
        }
        response = await auth_client.post("/api/v1/services", json=salon_payload)
        assert response.status_code == 201
        assert response.json()["category_id"] == serviceCategoryID

    async def test_service_get(self, auth_client):
        response = await auth_client.get(f"/api/v1/services/{TestService.serviceID}")
        assert response.status_code == 200
        assert response.json()["name"] == "SOME NAME"

    async def test_service_get_not_found(self, auth_client):
        response = await auth_client.get("/api/v1/services/9999")
        assert response.status_code == 404

    async def test_service_patch(self, auth_client):
        patch_payload = {
            "id": 1,
            "price": 100
        }
        response = await auth_client.patch("/api/v1/services", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["price"] == 100

    async def test_service_patch_with_no_existing_category(self, auth_client):
        patch_payload = {
            "id": 1,
            "category_id": 9999
        }
        response = await auth_client.patch("/api/v1/services", json=patch_payload)
        assert response.status_code == 404

    async def test_service_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/services/get-all", json={})
        print(response.json())
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_service_patch_set_archived(self, auth_client):
        patch_payload = {
            "id": 1,
            "archived": True
        }
        response = await auth_client.patch("/api/v1/services", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["archived"] == True