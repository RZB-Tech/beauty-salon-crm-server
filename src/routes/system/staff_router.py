from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_admin
from src.core.dependencies.uow import make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.staff.create import StaffCreateAPISchema
from src.schemas.staff.request import StaffPermissionsUpdateSchema, StaffRolesAssignSchema
from src.schemas.staff.response import StaffCreateResponseSchema, StaffResponseSchema
from src.services.auth.staff_service import StaffService

router = APIRouter(dependencies = [Depends(require_admin)])
get_staff_service = make_service_dependency(StaffService)

@router.post(
    "/create-user",
    response_model = StaffCreateResponseSchema,
    status_code = 201,
    summary = "Create a new staff member"
)
async def create_user(data: StaffCreateAPISchema,
                      staffService: StaffService = Depends(get_staff_service)):
    return await staffService.create(data)

@router.post(
    "/get-all",
    response_model = PaginatedResponseSchema[StaffResponseSchema],
    status_code = 200,
    summary = "Get all staff members"
)
async def get_all(params: RequestAllObject,
                  staffService: StaffService = Depends(get_staff_service)):
    return await staffService.get_all(params)

@router.patch(
    "/roles",
    response_model = StaffResponseSchema,
    status_code = 200,
    summary = "Assign roles to a staff member"
)
async def assign_roles(data: StaffRolesAssignSchema,
                 staffService: StaffService = Depends(get_staff_service)):
    return await staffService.assign_roles(data)

@router.patch(
    "/permissions",
    response_model = StaffResponseSchema,
    status_code = 200,
    summary = "Set a staff member's direct permission overrides"
)
async def update_permissions(data: StaffPermissionsUpdateSchema,
                 staffService: StaffService = Depends(get_staff_service)):
    return await staffService.update_permissions(data)