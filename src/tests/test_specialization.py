import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestSpecialization:
    specializationID: int

    async def test_specialization_create(self, auth_client):
        salon_payload = {
            "name": "SOME NAME"
        }
        response = await auth_client.post("/api/v1/specializations", json=salon_payload)
        TestSpecialization.specializationID = int(response.json()["id"])
        assert response.status_code == 201

    async def test_specialization_duplicate_name(self, auth_client):
        salon_payload = {
            "name": "SOME NAME"
        }
        response = await auth_client.post("/api/v1/specializations", json=salon_payload)
        assert response.status_code == 409

    async def test_specialization_get(self,auth_client):
        response = await auth_client.get(f"/api/v1/specializations/{TestSpecialization.specializationID}")
        assert response.status_code == 200
        assert response.json()["name"] == "SOME NAME"

    async def test_specialization_get_not_found(self, auth_client):
        response = await auth_client.get("/api/v1/specializations/9999")
        assert response.status_code == 404

    async def test_specialization_patch(self, auth_client):
        patch_payload = {
            "id": TestSpecialization.specializationID,
            "name": "NEW NAME"
        }
        response = await auth_client.patch("/api/v1/specializations", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["name"] == "NEW NAME"

    async def test_specialization_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/specializations/get-all", json={})
        print(response.json())
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_specialization_patch_set_archived(self, auth_client):
        patch_payload = {
            "id": TestSpecialization.specializationID,
            "archived": True
        }
        response = await auth_client.patch("/api/v1/specializations", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["archived"] == True

    # async def test_specialization_delete(self, auth_client):
    #     response = await auth_client.delete(f"/api/v1/specializations/{TestSpecialization.specializationID}")
    #     assert response.status_code == 204

    #     check_response = await auth_client.get(f"/api/v1/specializations/{TestSpecialization.specializationID}")
    #     assert check_response.status_code == 404