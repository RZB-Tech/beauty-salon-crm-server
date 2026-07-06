from fastapi import HTTPException, status

from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.employee.employee_model import Employee
from src.repository.staff.staff_model import Staff
from src.schemas.staff.create import StaffCreateAPISchema
from src.core.auth.security import hash_password, verify_password
from src.schemas.staff.request import StaffRequestSchema

class StaffService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: StaffCreateAPISchema) -> Staff:
        checkLogin = await self.uow.staffs.get(data.login)
        if checkLogin: raise HTTPException(409)

        employee: Employee | None
        if data.employee_id: 
            employee = await self.uow.employees.get(data.employee_id)
            if employee is None: raise HTTPException(404)

        if employee: staffData = data.model_dump(exclude = {"password", "firstname", "lastname", "middlename"})
        else: staffData = data.model_dump(exclude = {"password"})
        staffData["hashed_password"] = hash_password(data.password)
        staffData["login"] = data.login.lower()

        staff = Staff(**staffData)
        return await self.uow.staffs.create(staff)

    async def get(self, data: StaffRequestSchema) -> Staff:
        result: Staff | None
        if data.login is not None:
            result = await self.uow.staffs.get(login = data.login.lower())
        else:
            result = await self.uow.staffs.get(id = data.id)
        if not result: raise HTTPException(404)
        return result