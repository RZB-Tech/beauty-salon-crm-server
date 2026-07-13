import pytest
import pytest_asyncio
from datetime import datetime

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestAppointment:
    serviceID: int
    employeeID: int
    clientID: int
    appointmentID: int
    materialID: int
    appointmentRecordID: int
    appointmentServiceID: int

    # Appointment tests

    async def test_appointment_create_only_with_client(self, auth_client):
        clientResponse = await auth_client.post("/api/v1/clients", json={
            "firstname": "for appointment test",
            "sex": "male"
        })
        TestAppointment.clientID = int(clientResponse.json()["id"])

        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-01-01T10:00:00",
            "end_time_est": "2026-01-01T11:00:00"
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        TestAppointment.appointmentID = int(response.json()["id"])
        assert response.status_code == 201

    async def test_appointment_create_client_time_conflict(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-01-01T10:30:00",
            "end_time_est": "2026-01-01T11:30:00"
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 409

    async def test_appointment_create_with_invalid_client(self, auth_client):
        appointmentPayload = {
            "client_id": 99999,
            "start_time_est": "2026-01-01T10:00:00",
            "end_time_est": "2026-01-01T11:00:00"
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 404
    
    async def test_appointment_create_with_service_and_employee(self, auth_client):
        serviceResponse = await auth_client.post("/api/v1/services", json={
            "name": "for appointment test",
            "price": 1000
        })
        TestAppointment.serviceID = int(serviceResponse.json()["id"])

        employeeResponse = await auth_client.post("/api/v1/employees", json={
            "firstname": "for appointment test",
            "birth_date": "1990-01-01",
            "phone": "123456789540",
            "services_ids": [TestAppointment.serviceID]
        })
        TestAppointment.employeeID = int(employeeResponse.json()["id"])

        workScheduleResponse = await auth_client.post("/api/v1/work-schedules", json={
            "employee_id": TestAppointment.employeeID,
            "day": "2026-07-12",
            "start_time": "01:24:01.976Z",
            "end_time": "23:24:01.976Z"
            })
        assert workScheduleResponse.status_code == 201

        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T10:24:13.128Z",
            "end_time_est": "2026-07-12T11:24:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "service_id": TestAppointment.serviceID
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 201

    async def test_appointment_create_with_invalid_employee(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T13:24:13.128Z",
            "end_time_est": "2026-07-12T14:24:13.128Z",
            "records": [
                {
                "employee_id": 99999,
                "services": [
                    {
                    "service_id": TestAppointment.serviceID
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 404

    async def test_appointment_create_with_invalid_service(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T10:24:13.128Z",
            "end_time_est": "2026-07-12T11:24:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "service_id": 99999
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 409

    async def test_appointment_create_with_workSchedule_conflict(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T00:24:13.128Z",
            "end_time_est": "2026-07-12T01:24:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "service_id": TestAppointment.serviceID
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 409

    async def test_appointment_create_with_price_changed(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T02:24:13.128Z",
            "end_time_est": "2026-07-12T03:24:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "service_id": TestAppointment.serviceID,
                    "price": 2000,
                    "price_changed_reason": "Test reason"
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 201
        assert response.json()["records"][0]["services"][0]["price"] == 2000

    async def test_appointment_create_with_price_changed_no_reason(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T04:24:13.128Z",
            "end_time_est": "2026-07-12T05:24:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "service_id": TestAppointment.serviceID,
                    "price": 2000
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 400

    async def test_appointment_create_with_quantity(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T06:24:13.128Z",
            "end_time_est": "2026-07-12T07:24:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "service_id": TestAppointment.serviceID,
                    "quantity": 2
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 201
        assert response.json()["records"][0]["services"][0]["quantity"] == 2
        assert response.json()["total_price"] == 2000

    async def test_appointment_create_with_material(self, auth_client):
        materialResponse = await auth_client.post("/api/v1/materials", json={
            "article": "for appointment test123",
            "name": "for appointment test123",
            "sell_price": 1000,
            "quantity": 10
        })
        TestAppointment.materialID = int(materialResponse.json()["id"])

        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T07:25:13.128Z",
            "end_time_est": "2026-07-12T07:30:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "material_id": TestAppointment.materialID,
                    "quantity": 2
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 201
        assert response.json()["total_price"] == 2000

    async def test_appointment_create_with_material_insufficient_quantity(self, auth_client):
        appointmentPayload = {
            "client_id": TestAppointment.clientID,
            "start_time_est": "2026-07-12T07:31:13.128Z",
            "end_time_est": "2026-07-12T07:35:13.128Z",
            "records": [
                {
                "employee_id": TestAppointment.employeeID,
                "services": [
                    {
                    "material_id": TestAppointment.materialID,
                    "quantity": 20
                    }
                ]
                }
            ]
        }
        response = await auth_client.post("/api/v1/appointments", json=appointmentPayload)
        assert response.status_code == 400

    # Appointment records tests

    async def test_appointmentRecord_create(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "service_id": TestAppointment.serviceID
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 201
        TestAppointment.appointmentRecordID = int(recordResponse.json()["id"])

    async def test_appointmentRecord_create_with_invalid_appointment(self, auth_client):
        recordPayload = {
            "appointment_id": 99999,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "service_id": TestAppointment.serviceID
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 404

    async def test_appointmentRecord_create_with_invalid_employee(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": 99999,
            "services": [
                {
                "service_id": TestAppointment.serviceID
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 404

    async def test_appointmentRecord_create_with_invalid_service(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "service_id": 99999
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 404

    async def test_appointmentRecord_with_invalid_employee_service(self, auth_client):
        newService = await auth_client.post("/api/v1/services", json={
            "name": "for appointment test new employee",
            "price": 1000
        })
        newServiceID = int(newService.json()["id"])

        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "service_id": newServiceID
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 409

    async def test_appointmentRecord_create_with_invalid_material(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "material_id": 99999,
                "quantity": 1
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 404

    async def test_appointmentRecord_create_with_material_insufficient_quantity(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "material_id": TestAppointment.materialID,
                "quantity": 100
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 400

    async def test_appointmentRecord_create_with_service_price_changed_no_reason(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "service_id": TestAppointment.serviceID,
                "quantity": 1,
                "price": 5000
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 400

    async def test_appointmentRecord_create_with_material_price_changed_no_reason(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "material_id": TestAppointment.materialID,
                "quantity": 1,
                "price": 5000
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 400

    async def test_appointmentRecord_only_service_or_material(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "service_id": TestAppointment.serviceID,
                "material_id": TestAppointment.materialID,
                "quantity": 1
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 400

    async def test_appointmentRecord_delete(self, auth_client):
        response = await auth_client.delete(f"/api/v1/appointments-records/{TestAppointment.appointmentRecordID}")
        assert response.status_code == 200

        # Verify the record is actually deleted
        getResponse = await auth_client.get(f"/api/v1/appointments/{TestAppointment.appointmentID}")
        assert TestAppointment.appointmentRecordID not in [record["id"] for record in getResponse.json()["records"]]

    # Appointment services

    async def test_appointmentServices_create(self, auth_client):
        recordPayload = {
            "appointment_id": TestAppointment.appointmentID,
            "employee_id": TestAppointment.employeeID,
            "services": [
                {
                "service_id": TestAppointment.serviceID
                }
            ]
        }
        recordResponse = await auth_client.post(f"/api/v1/appointments-records", json=recordPayload)
        assert recordResponse.status_code == 201

        data = recordResponse.json()
        latest_record = max(
            data["records"],
            key=lambda record: datetime.fromisoformat(
                record["created_at"].replace("Z", "+00:00")
            )
        )
        TestAppointment.appointmentRecordID = int(latest_record["id"])

        appointmentServicePayload = {
            "appointment_record_id": TestAppointment.appointmentRecordID,
            "service_id": TestAppointment.serviceID
        }

        response = await auth_client.post("/api/v1/appointments-services", json=appointmentServicePayload)
        assert response.status_code == 201

        latest_service = max(
            latest_record["services"],
            key=lambda service: datetime.fromisoformat(
                service["created_at"].replace("Z", "+00:00")
            )
        )
        TestAppointment.appointmentServiceID = int(latest_service["id"])

    async def test_appointmentServices_create_invalid_appointment_record(self, auth_client):
        appointmentServicePayload = {
            "appointment_record_id": 99999,
            "service_id": TestAppointment.serviceID
        }
        response = await auth_client.post("/api/v1/appointments-services", json=appointmentServicePayload)
        assert response.status_code == 404

    async def test_appointmentServices_create_service_and_material_incompatible(self, auth_client):
        appointmentServicePayload = {
            "appointment_record_id": TestAppointment.appointmentRecordID,
            "service_id": TestAppointment.serviceID,
            "material_id": TestAppointment.materialID
        }
        response = await auth_client.post("/api/v1/appointments-services", json=appointmentServicePayload)
        assert response.status_code == 400

    async def test_appointmentServices_create_invalid_service(self, auth_client):
        appointmentServicePayload = {
            "appointment_record_id": TestAppointment.appointmentRecordID,
            "service_id": 99999
        }
        response = await auth_client.post("/api/v1/appointments-services", json=appointmentServicePayload)
        assert response.status_code == 404

    async def test_appointmentServices_create_invalid_service_employee(self, auth_client):
        newTestService = await auth_client.post("/api/v1/services", json = {
            "name": "newTestService1",
            "price": 1000
        })
        assert newTestService.status_code == 201
        testServiceID = int(newTestService.json()["id"])

        appointmentServicePayload = {
            "appointment_record_id": TestAppointment.appointmentRecordID,
            "service_id": testServiceID
        }
        response = await auth_client.post("/api/v1/appointments-services", json=appointmentServicePayload)
        print(response.json())
        assert response.status_code == 409
    