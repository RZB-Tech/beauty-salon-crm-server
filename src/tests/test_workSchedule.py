import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestWorkSchedule:
    workScheduleID: int
    employeeID: int

    async def test_workSchedule_create(self, auth_client):
        employeeResponse = await auth_client.post("/api/v1/employees",
            json= {
            "firstname": "SOME NAME",
            "lastname": "SOME LASTNAME",
            "birth_date": "1990-01-01",})
        TestWorkSchedule.employeeID = int(employeeResponse.json()["id"])

        salon_payload = {
            "employee_id": TestWorkSchedule.employeeID,
            "work_schedules": [
                {"day": 1, "start_time": "09:00:00", "end_time": "17:00:00"},
                {"day": 2, "start_time": "09:00:00", "end_time": "17:00:00"},
            ]
        }
        response = await auth_client.post("/api/v1/work-schedules", json=salon_payload)
        assert response.status_code == 201
        body = response.json()
        assert body["employee_id"] == TestWorkSchedule.employeeID
        assert sorted(schedule["day"] for schedule in body["work_schedules"]) == [1, 2]
        TestWorkSchedule.workScheduleID = int(body["work_schedules"][0]["id"])

    async def test_workSchedule_create_duplicate_day_in_payload(self, auth_client):
        salon_payload = {
            "employee_id": TestWorkSchedule.employeeID,
            "work_schedules": [
                {"day": 3, "start_time": "09:00:00", "end_time": "17:00:00"},
                {"day": 3, "start_time": "10:00:00", "end_time": "18:00:00"},
            ]
        }
        response = await auth_client.post("/api/v1/work-schedules", json=salon_payload)
        assert response.status_code == 400

    async def test_workSchedule_duplicate_day(self, auth_client):
        salon_payload = {
            "employee_id": TestWorkSchedule.employeeID,
            "work_schedules": [
                {"day": 1, "start_time": "09:00:00", "end_time": "17:00:00"},
            ]
        }
        response = await auth_client.post("/api/v1/work-schedules", json=salon_payload)
        assert response.status_code == 409

    async def test_workSchedule_get(self,auth_client):
        response = await auth_client.get(f"/api/v1/work-schedules/{TestWorkSchedule.workScheduleID}")
        assert response.status_code == 200
        body = response.json()
        assert body["employee_id"] == TestWorkSchedule.employeeID
        assert len(body["work_schedules"]) == 1
        assert body["work_schedules"][0]["id"] == TestWorkSchedule.workScheduleID

    async def test_workSchedule_get_not_found(self, auth_client):
        response = await auth_client.get("/api/v1/work-schedules/9999")
        assert response.status_code == 404

    async def test_workSchedule_patch(self, auth_client):
        patch_payload = {
            "work_schedules": [
                {"id": TestWorkSchedule.workScheduleID, "day": 1, "start_time": "10:00:00", "end_time": "17:00:00"},
            ]
        }
        response = await auth_client.patch("/api/v1/work-schedules", json=patch_payload)
        assert response.status_code == 200
        body = response.json()
        assert body["work_schedules"][0]["start_time"] == "10:00:00"
        assert body["work_schedules"][0]["day"] == 1
        assert int(body["work_schedules"][0]["id"]) == TestWorkSchedule.workScheduleID

    async def test_workSchedule_patch_not_found(self, auth_client):
        patch_payload = {
            "work_schedules": [
                {"id": 9999, "day": 5, "start_time": "10:00:00", "end_time": "17:00:00"},
            ]
        }
        response = await auth_client.patch("/api/v1/work-schedules", json=patch_payload)
        assert response.status_code == 404

    async def test_workSchedule_get_all(self, auth_client):
        response = await auth_client.post("/api/v1/work-schedules/get-all", json={})
        print(response.json())
        assert response.status_code ==  200
        assert len(response.json()["items"]) >= 1

    async def test_get_employee_workSchedule(self, auth_client):
        response = await auth_client.get(f"/api/v1/employees/{TestWorkSchedule.employeeID}/work-schedules")
        assert response.status_code == 200
        assert len(response.json()["work_schedules"]) >= 1

    async def test_delete_workSchedule(self, auth_client):
        response = await auth_client.delete(f"/api/v1/work-schedules/{TestWorkSchedule.workScheduleID}")
        assert response.status_code == 204
