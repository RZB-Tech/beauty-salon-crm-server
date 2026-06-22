import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio

# @pytest_asyncio.fixture
# async def create_employee(async_client):
#     employee_payload = {
#         "firstname": "Adrian",
#         "lastname": "Smith",
#         "birthDate": "1995-05-15"
#     }
#     emp_response = await async_client.post("/api/v1/employees/", json=employee_payload)
#     assert emp_response.status_code == 201
    
#     return emp_response.json()

# async def test_create_workSchedule(async_client, create_employee):
#     schedule_payload = {
#         "employee_id": create_employee["id"],
#         "day": "2026-07-14",
#         "start_time": "09:00:00",
#         "end_time": "17:00:00"
#     }
#     sched_response = await async_client.post("/api/v1/work-schedules/", json=schedule_payload)
#     assert sched_response.status_code == 201
#     assert sched_response.json()["start_time"] == "09:00:00"
    

# async def test_cannot_create_schedule_with_invalid_times(async_client):
#     """This tests our Pydantic validation / DB Constraints!"""
    
#     # Notice start_time is AFTER end_time
#     bad_payload = {
#         "employee_id": 1, # Assuming employee 1 exists from previous test
#         "day": "2026-07-15",
#         "start_time": "18:00:00",
#         "end_time": "10:00:00" 
#     }
    
#     response = await async_client.post("/api/v1/work-schedules/", json=bad_payload)
    
#     # We expect our Pydantic validator to catch this and throw a 422!
#     assert response.status_code == 422 
#     assert "start_time must be strictly before end_time" in response.text