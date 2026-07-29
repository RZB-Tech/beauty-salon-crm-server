from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.work_schedule.create import AbsenceCreateSchema
from src.schemas.work_schedule.response import AbsenceResponseSchema
from src.schemas.work_schedule.update import AbsenceUpdateSchema
from src.services.employee.absence_service import EmployeeAbsenceService

router = APIRouter()

get_absence_service = make_service_dependency(EmployeeAbsenceService)

@router.post(
    "",
    response_model=AbsenceResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отсутствие",
    description="Регистрирует отсутствие сотрудника (`absence_type`: sick / vacation / day off / weekend / other) на период с `start_date` по `end_date`.",
    dependencies=[Depends(require_permission([PermissionCode.ABSENCE_CREATE]))]
)
async def create(data: AbsenceCreateSchema,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.create(data)

@router.patch(
    "",
    response_model=AbsenceResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Обновить отсутствие",
    description="Обновляет период, тип, причину или статус архивации отсутствия по его `id`.",
    dependencies=[Depends(require_permission([PermissionCode.ABSENCE_UPDATE]))]
)
async def update(data: AbsenceUpdateSchema,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.update(data)

@router.post(
    "/get-all",
    response_model = PaginatedResponseSchema[AbsenceResponseSchema],
    status_code = 200,
    summary="Получить все отсутствия",
    description="Возвращает постраничный список отсутствий сотрудников с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.ABSENCE_READ]))]
)
async def get_all(params: RequestAllObject,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.get_all(params)

@router.get(
    "/{id}",
    response_model=AbsenceResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить отсутствие по ID",
    description="Возвращает отсутствие по его `id`.",
    dependencies=[Depends(require_permission([PermissionCode.ABSENCE_READ]))]
)
async def get(id: int,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.get(id)

# @router.delete(
#     "/{id}",
#     status_code = status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(require_permission([PermissionCode.ABSENCE_DELETE]))]
# )
# async def delete(id: int,
#                  absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
#     return await absenceService.delete(id)