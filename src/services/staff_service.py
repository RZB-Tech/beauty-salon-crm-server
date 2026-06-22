from fastapi import HTTPException, status

from src.core.dependencies.uow import UnitOfWork
from src.repository.staff.staff_model import Staff
from src.schemas.staff.create import StaffCreateAPISchema
from src.core.auth.security import hash_password

class StaffService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: StaffCreateAPISchema) -> Staff:
        staffData = data.model_dump(exclude = {"password"})
        staffData["hashed_password"] = hash_password(data.password)
        staffData["login"] = data.login.lower()

        staff = Staff(**staffData)

        return await self.uow.staffs.create(staff)

    async def get(self, login: str) -> Staff:
        result = await self.uow.staffs.get(login.lower())
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )
        return result
