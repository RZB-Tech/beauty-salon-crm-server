from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
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
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_CREATE]))]
)
async def create(data: WorkScheduleCreateSchema,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.create(data)

@router.patch(
    "",
    response_model=WorkScheduleResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update category",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_UPDATE]))]
)
async def update(data: WorkScheduleUpdateSchema,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[WorkScheduleResponseSchema],
    status_code = 200,
    summary="Get all categories",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_READ]))]
)
async def get_all(params: RequestAllObject,
                  workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.get_all(params)

@router.get(
    "/{id}",
    response_model=WorkScheduleResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get ",
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_READ]))]
)
async def get(id: int,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.get(id)

@router.delete(
    "/{id}",
    status_code = 204,
    dependencies=[Depends(require_permission([PermissionCode.WORK_SCHEDULE_DELETE]))]
)
async def delete(id: int,
                 workScheduleService: WorkScheduleService = Depends(get_workSchedule_service)):
    return await workScheduleService.delete(id)