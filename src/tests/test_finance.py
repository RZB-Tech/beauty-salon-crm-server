from datetime import datetime
import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestPayroll:
    payrollID: int
    payoutID: int
    transactionID: int
    employeeID: int

    # Payroll

    async def test_payroll_create(self, auth_client):
        employeeResponse = await auth_client.post("/api/v1/employees", 
            json= {
            "firstname": "SOME NAME",
            "lastname": "SOME LASTNAME",
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

    async def test_payroll_cancel_invalid(self, auth_client):
        response = await auth_client.post(f"/api/v1/payrolls/cancel?id={TestPayroll.payrollID}")
        assert response.status_code == 400

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

    # Payout

    async def test_payout_create(self, auth_client):
        payrollPayload = {
            "employee_id": TestPayroll.employeeID,
            "amount": 1000,
            "type": "bonus"
        }
        response = await auth_client.post("/api/v1/payrolls", json=payrollPayload)
        TestPayroll.payrollID = int(response.json()["id"])
        assert response.status_code == 201

        payoutPayload = {
            "employee_id": TestPayroll.employeeID,
            "type": "other",
            "method": "cash",
        }
        response = await auth_client.post("/api/v1/payouts", json=payoutPayload)
        TestPayroll.payoutID = int(response.json()["id"])
        assert response.status_code == 201

    async def test_payroll_cancel_with_payout(self, auth_client):
        response = await auth_client.post(f"/api/v1/payrolls/cancel?id={TestPayroll.payrollID}")
        assert response.status_code == 409

    async def test_payout_get(self, auth_client):
        response = await auth_client.get(f"/api/v1/payouts/{TestPayroll.payoutID}")
        assert response.status_code == 200
        assert response.json()["id"] == TestPayroll.payoutID

    async def test_payout_get_not_found(self, auth_client):
        response = await auth_client.get("/api/v1/payouts/9999")
        assert response.status_code == 404

    async def test_payout_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/payouts/get-all", json={})
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1

    # Transaction

    async def test_payout_transaction_created(self, auth_client):
        response = await auth_client.post("/api/v1/transactions/get-all", json={})
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1
        latest_transaction = max(
            response.json()["items"],
            key=lambda transaction: datetime.fromisoformat(
                transaction["created_at"].replace("Z", "+00:00")
            )
        )
        assert response.status_code == 200
        assert latest_transaction["payout_id"] == TestPayroll.payoutID
        assert latest_transaction["auto_generated"] == True
        TestPayroll.transactionID = int(latest_transaction["id"])

    async def test_transaction_cancel_auto_generated(self, auth_client):
        response = await auth_client.post(f"/api/v1/transactions/{TestPayroll.transactionID}/cancel")
        assert response.status_code == 400