import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestPayroll:
    payrollID: int
    employeeID: int

    async def test_payroll_create(self, auth_client):
        employeeResponse = await auth_client.post("/api/v1/employees", 
            json= {
            "firstname": "SOME NAME",
            "birth_date": "1990-01-01",})
        TestPayroll.employeeID = int(employeeResponse.json()["id"])

        salon_payload = {
            "employee_id": TestPayroll.employeeID,
            "amount": 1000,
            "type": "bonus"
        }
        response = await auth_client.post("/api/v1/payrolls", json=salon_payload)
        TestPayroll.payrollID = int(response.json()["id"])
        assert response.status_code == 201

    async def test_payroll_get(self,auth_client):
        response = await auth_client.get(f"/api/v1/payrolls/{TestPayroll.payrollID}")
        assert response.status_code == 200

    async def test_payroll_get_not_found(self, auth_client):
        response = await auth_client.get("/api/v1/payrolls/9999")
        assert response.status_code == 404

    async def test_payroll_patch(self, auth_client):
        patch_payload = {
            "id": TestPayroll.payrollID,
            "amount": 1500
        }
        response = await auth_client.patch("/api/v1/payrolls", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["amount"] == 1500

    async def test_payroll_patch_with_invalid_type(self, auth_client):
        patch_payload = {
            "id": TestPayroll.payrollID,
            "type": "invalid_type"
        }
        response = await auth_client.patch("/api/v1/payrolls", json=patch_payload)
        assert response.status_code == 422

    async def test_payroll_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/payrolls/get-all", json={})
        print(response.json())
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_payroll_cancel(self, auth_client):
        response = await auth_client.post(f"/api/v1/payrolls/cancel?id={TestPayroll.payrollID}")
        assert response.status_code == 200
        print(response.json())
        assert response.json()["status"] == "cancelled"

    async def test_payroll_patch_set_archived(self, auth_client):
        patch_payload = {
            "id": TestPayroll.payrollID,
            "archived": True
        }
        response = await auth_client.patch("/api/v1/payrolls", json=patch_payload)
        assert response.status_code == 200
        assert response.json()["archived"] == True

    async def delete(self, auth_client):
        response = await auth_client.delete(f"/api/v1/payrolls/{TestPayroll.payrollID}")
        assert response.status_code == 204