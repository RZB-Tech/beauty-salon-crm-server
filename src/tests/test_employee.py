import pytest
pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestEmployee:

    employeeID: int
    serviceID: int
    specizalizationID: int

    async def test_employee_create(self, auth_client):
        salon_payload = {
            "firstname": "SOME NAME",
            "birth_date": "1990-01-01",
            "phone": "1234567890",
        }
        response = await auth_client.post("/api/v1/employees", json=salon_payload)
        assert response.status_code == 201
        TestEmployee.employeeID = int(response.json()["id"])

    async def test_employee_duplicate_phone(self, auth_client):
        salon_payload = {
            "firstname": "SOME NAME",
            "birth_date": "1990-01-01",
            "phone": "1234567890",
        }
        response = await auth_client.post("/api/v1/employees", json=salon_payload)
        assert response.status_code == 409

    async def test_employee_create_with_specialization(self, auth_client):
        specialization = await auth_client.post("/api/v1/specializations", json={"name": "for employee test"})
        specializationID = int(specialization.json()["id"])
        salon_payload = {
            "firstname": "SOME NAME 2",
            "birth_date": "1990-01-01",
            "phone": "0987654321",
            "specialization_id": specializationID
        }
        response = await auth_client.post("/api/v1/employees", json=salon_payload)
        assert response.status_code == 201
        assert response.json()["specialization_id"] == specializationID

    async def test_employee_create_with_service(self, auth_client):
        service = await auth_client.post("/api/v1/services", json={"name": "for employee test"})
        TestEmployee.serviceID = int(service.json()["id"])
        salon_payload = {
            "firstname": "SOME NAME 3",
            "birth_date": "1990-01-01",
            "phone": "1122334455",
            "services_ids": [TestEmployee.serviceID]
        }
        response = await auth_client.post("/api/v1/employees", json=salon_payload)
        assert response.status_code == 201

        responseServices = response.json()["services"]
        services: list[int] = []
        for i in responseServices or []: services.append(i["id"])
        assert TestEmployee.serviceID in services

    async def test_employee_create_with_invalid_service(self, auth_client):
        salon_payload = {
            "firstname": "SOME NAME 4",
            "birth_date": "1990-01-01",
            "phone": "5566778899",
            "services_ids": [99999]
        }
        response = await auth_client.post("/api/v1/employees", json=salon_payload)
        assert response.status_code == 404

    async def test_employee_create_with_invalid_specialization(self, auth_client):
        salon_payload = {
            "firstname": "SOME NAME 5",
            "birth_date": "1990-01-01",
            "phone": "6677889900",
            "specialization_id": 99999
        }
        response = await auth_client.post("/api/v1/employees", json=salon_payload)
        assert response.status_code == 404

    async def test_employee_get(self, auth_client):
        response = await auth_client.get(f"/api/v1/employees/{TestEmployee.employeeID}")
        assert response.status_code == 200

    async def test_employee_get_not_found(self, auth_client):
        response = await auth_client.get(f"/api/v1/employees/99999")
        assert response.status_code == 404

    async def test_employee_patch(self, auth_client):
        patch_payload = {
            "id": TestEmployee.employeeID,
            "firstname": "UPDATED NAME"
        }
        response = await auth_client.patch(f"/api/v1/employees", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["firstname"] == "UPDATED NAME"

    async def test_employee_patch_with_invalid_service(self, auth_client):
        patch_payload = {
            "id": TestEmployee.employeeID,
            "services": [99999]
        }
        response = await auth_client.patch(f"/api/v1/employees", json=patch_payload)
        assert response.status_code == 404

    async def test_employee_patch_with_invalid_specialization(self, auth_client):
        patch_payload = {
            "id": TestEmployee.employeeID,
            "specialization_id": 99999
        }
        response = await auth_client.patch(f"/api/v1/employees", json=patch_payload)
        assert response.status_code == 404

    async def test_employee_patch_with_service(self, auth_client):
        service = await auth_client.post("/api/v1/services", json={"name": "for employee test patch"})
        newServiceID = int(service.json()["id"])
        patch_payload = {
            "id": TestEmployee.employeeID,
            "services": [TestEmployee.serviceID, newServiceID]
        }
        response = await auth_client.patch(f"/api/v1/employees", json=patch_payload)
        assert response.status_code == 200

        responseServices = response.json()["services"]
        services: list[int] = []
        for i in responseServices or []: services.append(i["id"])
        assert TestEmployee.serviceID, newServiceID in services

    async def test_employee_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/employees/get-all", json={})
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_employee_patch_set_archived(self, auth_client):
        patch_payload = {
            "id": TestEmployee.employeeID,
            "archived": True
        }
        response = await auth_client.patch(f"/api/v1/employees", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["archived"] == True

    async def test_employee_patch_archived(self, auth_client):
        patch_payload = {
            "id": TestEmployee.employeeID,
            "firstname": "UPDATED NAME"
        }
        response = await auth_client.patch(f"/api/v1/employees", json=patch_payload)
        assert response.status_code == 409