import pytest
pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestMaterial:
    materialID: int
    async def test_create_material(self, auth_client):
        salon_payload = {
            "article": "MT-ASAD",
            "name": "SOME NAME"
        }
        response = await auth_client.post("/api/v1/materials", json=salon_payload)
        assert response.status_code == 201
        TestMaterial.materialID = int(response.json()["id"])

    async def test_create_material_duplicate_article(self, auth_client):
        salon_payload = {
            "article": "MT-ASAD",
            "name": "SOME NAMI"
        }
        response = await auth_client.post("/api/v1/materials", json=salon_payload)
        assert response.status_code == 409

    async def test_get_material(self, auth_client):
        response = await auth_client.get(f"/api/v1/materials/{TestMaterial.materialID}")
        print(response.json())
        assert response.status_code == 200
        assert response.json()["article"] == "MT-ASAD"

    async def test_get_material_not_found(self, auth_client):
        response = await auth_client.get(f"/api/v1/materials/{999}")
        assert response.status_code == 404

    async def test_patch_material(self,auth_client):
        patch_payload = {
            "id": TestMaterial.materialID,
            "description": "NEW NAME"
        }
        response = await auth_client.patch("/api/v1/materials", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["description"] == "NEW NAME"

    async def test_get_all_materials(self, auth_client):
        response = await auth_client.post("/api/v1/materials/get-all", json={})
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_patch_material_set_archived(self, auth_client):
        patch_payload = {
            "id": TestMaterial.materialID,
            "archived": True
        }
        response = await auth_client.patch("/api/v1/materials", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["archived"] == True

    async def test_material_update_quantity(self, auth_client):
        payload = {
            "id": TestMaterial.materialID,
            "quantity": 10,
            "operation": 1
        }
        response = await auth_client.post("/api/v1/materials/update-quantity", json=payload)
        assert response.status_code == 200
        assert response.json()["quantity"] == 10

        payload = {
            "id": TestMaterial.materialID,
            "quantity": 5,
            "operation": -1
        }
        response = await auth_client.post("/api/v1/materials/update-quantity", json=payload)
        assert response.status_code == 200
        assert response.json()["quantity"] == 5

        payload = {
            "id": TestMaterial.materialID,
            "quantity": 6,
            "operation": -1
        }
        response = await auth_client.post("/api/v1/materials/update-quantity", json=payload)
        assert response.status_code == 409