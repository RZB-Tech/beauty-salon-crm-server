from httpx import AsyncClient
import pytest
from datetime import datetime, time, timedelta
from src.repository import Client, Employee, Service, WorkSchedule
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords, AppointmentServices

pytestmark = pytest.mark.asyncio

# def createTempData(client: Client = None, 
#                    service: Service = None,
#                    employee: Employee = None,
#                    workSchedule: WorkSchedule = None)

@pytest.mark.asyncio
async def test_create_appointment_with_client(async_client: AsyncClient, db_session):
    # create service
    # servicePayload = {
    #     "name": "Haircut"
    # }
    # serviceResponse = await async_client.post("/api/v1/services/", json=servicePayload)
    # assert serviceResponse.status_code == 201
    # service = serviceResponse.json()

    # # create employee
    # employeePayload = {
    #     "firstname": "Adrian",
    #     "lastname": "Smith",
    #     "birthDate": "1995-05-15"
    # }
    # employeeResponse = await async_client.post("/api/v1/employees/", json=employeePayload)
    # assert employeeResponse.status_code == 201
    # employee = employeeResponse.json()

    # # assign service to employee
    # employeePayload = {
    #     "id": employee["id"],
    #     "services": [service["id"]]
    # }
    # employeeResponse = await async_client.patch("/api/v1/employees/", json = employeePayload)
    # assert employeeResponse.status_code == 200
    # employee = employeeResponse.json()

    # # create client 
    # clientPayload = {
    #     "firstname": "Eva",
    #     "sex": "female"
    # }
    # clientResponse = await async_client.post("/api/v1/clients/", json=clientPayload)
    # assert clientResponse.status_code == 201
    # client = clientResponse.json()

    # # create work schedule
    # schedulePayload = {
    #     "employee_id": employee["id"],
    #     "day": "2026-07-14",
    #     "start_time": "09:00:00",
    #     "end_time": "17:00:00"
    # }
    # scheduleResponse = await async_client.post("/api/v1/work-schedules/", json=schedulePayload)
    # assert scheduleResponse.status_code == 201

    client = Client(firstname = "Maxim", sex = "male")
    db_session.add(client)

    service = Service(name = "Haircut")
    db_session.add(service)

    employee = Employee(firstname = "John", birth_date = datetime(1999, 9, 9).date(), services = [service])
    db_session.add(employee)

    await db_session.flush()

    schedule = WorkSchedule(employee_id = employee.id, 
                            day = datetime(2026, 6, 15).date(),
                            start_time = time(9, 0),
                            end_time = time(18, 0))
    db_session.add(schedule)

    await db_session.commit()

    # create appointment without services
    appointmentPayload = {
        "client_id": client.id,
        "start_time_est": datetime.now().isoformat(),
        "end_time_est": (datetime.now() + timedelta(hours = 1)).isoformat()
    }
    appointmentResponse = await async_client.post("/api/v1/appointments/", json=appointmentPayload)
    assert appointmentResponse.status_code == 201

@pytest.mark.asyncio
async def test_get_appointment(async_client: AsyncClient, db_session):
    client = Client(firstname = "Maxim", sex = "male")
    db_session.add(client)

    service = Service(name = "Haircut")
    db_session.add(service)

    employee = Employee(firstname = "John", birth_date = datetime(1999, 9, 9).date(), services = [service])
    db_session.add(employee)

    await db_session.flush()

    schedule = WorkSchedule(employee_id = employee.id, 
                            day = datetime(2026, 6, 15).date(),
                            start_time = time(9, 0),
                            end_time = time(18, 0))
    db_session.add(schedule)

    await db_session.flush()

    appointment = Appointment(
        client_id=client.id,
        start_time_est=datetime(2026, 6, 15, 10, 0),  # Static time string
        end_time_est=datetime(2026, 6, 15, 11, 0),
        records=[
            AppointmentRecords(
                employee_id=employee.id,
                services=[AppointmentServices(
                    service_id=service.id,
                    price = 1000)
                ]
            )
        ]
    )
    db_session.add(appointment)

    await db_session.commit()

    findAppointment = await async_client.get(f"/api/v1/appointments/{appointment.id}")
    assert findAppointment.status_code == 200

# @pytest.mark.asyncio
# async def test_create_appointment_with_payments(async_client: AsyncClient, db_session):
