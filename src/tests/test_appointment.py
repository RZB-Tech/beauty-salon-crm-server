import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestAppointment:
    serviceID: int
    employeeID: int
    clientID: int
    appointmentID: int
    materialID: int

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
