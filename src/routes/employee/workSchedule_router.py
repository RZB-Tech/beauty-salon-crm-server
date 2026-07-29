from datetime import date

from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.employee.response import EmployeeResponseBase
from src.schemas.work_schedule.create import WorkScheduleCreateSchema
from src.schemas.work_schedule.response import WorkScheduleResponseSchema
from src.schemas.work_schedule.update import WorkScheduleUpdateSchema
from src.services.employee.workSchedule_service import WorkScheduleService

router = APIRouter()

get_workSchedule_service = make_service_dependency(WorkScheduleService)

@router.post(
    "",
    response_model=WorkScheduleResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать график работы сотрудника",
    description="Создает график работы сотрудника на выбранные дни недели (`day`: 1-7, дни не должны повторяться). Время окончания должно быть строго позже времени начала.",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_CREATE]))]
)
async def create(data: WorkScheduleCreateSchema,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.create(data)

@router.patch(
    "",
    response_model=WorkScheduleResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Обновить график работы",
    description="Обновляет время начала/окончания указанных элементов графика работы по их `id`.",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_UPDATE]))]
)
async def update(data: WorkScheduleUpdateSchema,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[WorkScheduleResponseSchema],
    status_code = 200,
    summary="Получить все графики работы",
    description="Возвращает постраничный список элементов графика работы с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_READ]))]
)
async def get_all(params: RequestAllObject,
                  workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.get_all(params)

@router.get(
    "/get-assigned-employees-by-date",
    status_code = 200,
    response_model = list[EmployeeResponseBase],
    summary = "Сотрудники, работающие в указанный день",
    description = "Возвращает список сотрудников, у которых на указанную дату (`day`) запланирована работа по графику.",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_READ]))]
)
async def get_assigned_employees_with_day(day: date,
                                          workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.getEmployeesByDate(day)

@router.get(
    "/{id}",
    response_model=WorkScheduleResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить график работы по ID",
    description="Возвращает элемент графика работы по его `id`.",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_READ]))]
)
async def get(id: int,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.get(id)

@router.delete(
    "/{id}",
    status_code = 204,
    summary = "Удалить элемент графика работы",
    description = "Безвозвратно удаляет элемент графика работы по его `id`.",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_DELETE]))]
)
async def delete(id: int,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.delete(id)