from datetime import datetime
import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestReceipt:
    employeeID: int
    clientID: int
    serviceID: int
    appointmentID: int
    receiptID: int
    paymentID: int
    transactionID: int

    # Payroll

    async def test_receipt_create(self, auth_client):
        serviceResponse = await auth_client.post("/api/v1/services", json = {
            "name": "for receipt service",
            "price": 1500
        })
        assert serviceResponse.status_code == 201
        TestReceipt.serviceID = int(serviceResponse.json()["id"])

        employeeResponse = await auth_client.post("/api/v1/employees", 
            json= {
            "firstname": "receipt SOME NAME",
            "lastname": "receipt SOME LASTNAME",
            "birth_date": "1990-01-01",
            "services_ids": [TestReceipt.serviceID]
        })
        assert employeeResponse.status_code == 201
        TestReceipt.employeeID = int(employeeResponse.json()["id"])

        workScheduleResponse = await auth_client.post("api/v1/work-schedules", json = {
            "employee_id": TestReceipt.employeeID,
            "day": "2026-07-13",
            "start_time": "01:00:00",
            "end_time": "23:00:00"
        })
        assert workScheduleResponse.status_code == 201

        clientPayload = {
            "firstname": "string",
            "sex": "male"
        }
        clientResponse = await auth_client.post("/api/v1/clients", json = clientPayload)
        assert clientResponse.status_code == 201
        TestReceipt.clientID = int(clientResponse.json()["id"])

        appointmentPayload = {
            "client_id": TestReceipt.clientID,
            "start_time_est": "2026-07-13T10:16:16.089Z",
            "end_time_est": "2026-07-13T11:16:16.089Z",
            "records": [
                {
                "employee_id": TestReceipt.employeeID,
                "services": [
                    {
                    "service_id": TestReceipt.serviceID
                    }
                ]
                }
            ]
        }
        appointmentResponse = await auth_client.post("/api/v1/appointments", json = appointmentPayload)
        assert appointmentResponse.status_code == 201
        TestReceipt.appointmentID = int(appointmentResponse.json()["id"])

        receiptPayload = {
            "receipt_type": "appointment",
            "appointment_id": TestReceipt.appointmentID
        }
        receiptResponse = await auth_client.post("/api/v1/receipts", json = receiptPayload)
        assert receiptResponse.status_code == 201
        assert receiptResponse.json()["total_amount"] == 1500
        TestReceipt.receiptID = int(receiptResponse.json()["id"])

    async def test_receipt_invalid_payment(self, auth_client):
        paymentPayload = {
            "receipt_id": TestReceipt.receiptID,
            "method": "invalid method"
        }
        paymentResponse = await auth_client.post("/api/v1/receipts/make_payment", json = paymentPayload)
        assert paymentResponse.status_code == 422

    async def test_receipt_make_full_payment(self, auth_client):
        paymentPayload = {
            "receipt_id": TestReceipt.receiptID,
            "method": "cash",
            "amount": 1500
        }
        paymentResponse = await auth_client.post("/api/v1/receipts/make_payment", json = paymentPayload)
        assert paymentResponse.status_code == 201
        assert paymentResponse.json()["paid_amount"] == 1500
        assert paymentResponse.json()["remaining_amount"] == 0

        appointmentResponse = await auth_client.get(f"/api/v1/appointments/{TestReceipt.appointmentID}")
        assert appointmentResponse.status_code == 200
        assert appointmentResponse.json()["paid"] == True

    async def test_receipt_payment_created_transaction(self, auth_client):
        transactionResponse = await auth_client.post("/api/v1/transactions/get-all", json = {})
        assert transactionResponse.status_code == 200
        assert len(transactionResponse.json()["items"]) >= 1

        latest_transaction = max(
            transactionResponse.json()["items"],
            key=lambda transaction: datetime.fromisoformat(
                transaction["created_at"].replace("Z", "+00:00")
            )
        )

        assert latest_transaction["receipt_id"] == TestReceipt.receiptID
        assert latest_transaction["amount"] == 1500

    async def test_receipt_make_part_payment(self, auth_client):
        appointmentPayload = {
            "client_id": TestReceipt.clientID,
            "start_time_est": "2026-07-13T11:20:16.089Z",
            "end_time_est": "2026-07-13T11:25:16.089Z",
            "records": [
                {
                "employee_id": TestReceipt.employeeID,
                "services": [
                    {
                    "service_id": TestReceipt.serviceID,
                    "price": 5000,
                    "price_changed_reason": "some reason"
                    }
                ]
                }
            ]
        }
        appointmentResponse = await auth_client.post("/api/v1/appointments", json = appointmentPayload)
        assert appointmentResponse.status_code == 201
        TestReceipt.appointmentID = int(appointmentResponse.json()["id"])

        receiptPayload = {
            "receipt_type": "appointment",
            "appointment_id": TestReceipt.appointmentID
        }
        receiptResponse = await auth_client.post("/api/v1/receipts", json = receiptPayload)
        assert receiptResponse.status_code == 201
        assert receiptResponse.json()["total_amount"] == 5000
        TestReceipt.receiptID = int(receiptResponse.json()["id"])

        paymentPayload = {
            "receipt_id": TestReceipt.receiptID,
            "method": "cash",
            "amount": 1500
        }
        paymentResponse = await auth_client.post("/api/v1/receipts/make_payment", json = paymentPayload)
        assert paymentResponse.status_code == 201
        assert paymentResponse.json()["paid_amount"] == 1500
        assert paymentResponse.json()["remaining_amount"] == 3500

        appointmentResponse = await auth_client.get(f"/api/v1/appointments/{TestReceipt.appointmentID}")
        assert appointmentResponse.status_code == 200
        assert appointmentResponse.json()["paid"] == False

    async def test_part_payment_created_transaction(self, auth_client):
        transactionResponse = await auth_client.post("/api/v1/transactions/get-all", json = {})
        assert transactionResponse.status_code == 200
        assert len(transactionResponse.json()["items"]) >= 1

        latest_transaction = max(
            transactionResponse.json()["items"],
            key=lambda transaction: datetime.fromisoformat(
                transaction["created_at"].replace("Z", "+00:00")
            )
        )

        assert latest_transaction["receipt_id"] == TestReceipt.receiptID
        assert latest_transaction["amount"] == 1500

    async def test_receipt_invalid_overpayment(self, auth_client):
        paymentPayload = {
            "receipt_id": TestReceipt.receiptID,
            "method": "cash",
            "amount": 10000,
            # by default, if payment has overpayment 
            # add redundant payment amount to client's deposit
            # field add_change_to_deposit by default is True
            "add_change_to_deposit": False
        }
        paymentResponse = await auth_client.post("/api/v1/receipts/make_payment", json = paymentPayload)
        assert paymentResponse.status_code == 400

    async def test_receipt_overpayment(self, auth_client):
        paymentPayload = {
            "receipt_id": TestReceipt.receiptID,
            "method": "cash",
            "amount": 10000
        }
        paymentResponse = await auth_client.post("/api/v1/receipts/make_payment", json = paymentPayload)
        assert paymentResponse.status_code == 201