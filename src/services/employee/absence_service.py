import math
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.absence_exceptions import AbsenceNotFound
from src.repository.employee.workSchedule_model import EmployeeAbsence
from src.schemas.base import RequestAllObject
from src.schemas.work_schedule.create import AbsenceCreateSchema
from src.schemas.work_schedule.update import AbsenceUpdateSchema

class EmployeeAbsenceService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    @require_exists("employees", target_param = "employee_id")
    async def create(self, data: AbsenceCreateSchema) -> EmployeeAbsence:
        absenceData = data.model_dump()
        newObject = EmployeeAbsence(**absenceData)
        return await self.uow.absences.create(newObject)

    @require_exists("absences")
    async def update(self, data: AbsenceUpdateSchema) -> EmployeeAbsence:
        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        result = await self.uow.absences.update(data.id, **dataDict)
        if result is None: raise AbsenceNotFound(data.id)
        return result
    
    async def get(self, id: int) -> EmployeeAbsence:
        result = await self.uow.absences.get(id)
        if not result: raise AbsenceNotFound(id)
        return result
    
    async def get_many(self, ids: list[int]) -> list[EmployeeAbsence]:
        return await self.uow.absences.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.absences.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    @require_exists("absences")
    async def delete(self, id: int) -> bool:
        return await self.uow.absences.delete(id)