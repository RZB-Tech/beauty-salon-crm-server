from httpx import AsyncClient
import pytest
from datetime import datetime, time, timedelta
from src.repository import Client, Employee, Service, WorkSchedule
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords, AppointmentServices
import pytest
from httpx import AsyncClient
from datetime import datetime, time

pytestmark = pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_appointment_via_http(async_client: AsyncClient):
    # 1. Login to retrieve authentication cookies
    login_payload = {
        "username": "admin",  # Adjust keys to match your Auth schema
        "password": "test"
    }
    login_response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200

    client_payload = {"firstname": "Maxim", "sex": "male"}
    client_res = await async_client.post("/api/v1/clients", json=client_payload)
    assert client_res.status_code == 201
    client_id = client_res.json()["id"]

    # 3. Create Service
    service_payload = {"name": "Haircut"}
    service_res = await async_client.post("/api/v1/services", json=service_payload)
    assert service_res.status_code == 201
    service_id = service_res.json()["id"]

    # 4. Create Employee (linking the service_id)
    employee_payload = {
        "firstname": "John",
        "birth_date": "1999-09-09",
        "service_ids": [service_id]  # Adjust key to match your Pydantic schema
    }
    employee_res = await async_client.post("/api/v1/employees", json=employee_payload)
    assert employee_res.status_code == 201
    employee_id = employee_res.json()["id"]

    # 5. Create Work Schedule
    schedule_payload = {
        "employee_id": employee_id,
        "day": "2026-06-15",
        "start_time": "09:00:00",
        "end_time": "18:00:00"
    }
    schedule_res = await async_client.post("/api/v1/schedules", json=schedule_payload)
    assert schedule_res.status_code == 201

    # 6. Create Appointment
    appointment_payload = {
        "client_id": client_id,
        "start_time_est": "2026-06-15T10:00:00",
        "end_time_est": "2026-06-15T11:00:00",
        "records": [
            {
                "employee_id": employee_id,
                "services": [
                    {
                        "service_id": service_id,
                        "price": 1000
                    }
                ]
            }
        ]
    }
    appointment_res = await async_client.post("/api/v1/appointments", json=appointment_payload)
    assert appointment_res.status_code == 201
    appointment_id = appointment_res.json()["id"]

    # 7. GET the newly created appointment
    find_appointment = await async_client.get(f"/api/v1/appointments/{appointment_id}")
    assert find_appointment.status_code == 200
    
    # Optional check to verify the structure matches
    data = find_appointment.json()
    assert data["id"] == appointment_id
    assert data["client_id"] == client_id
