from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payroll.create import PayrollCreateSchema
from src.schemas.payroll.response import PayrollResponseSchema
from src.schemas.payroll.update import PayrollUpdateSchema
from src.services.payment.payroll_service import PayrollService

router = APIRouter()

get_payroll_service = make_service_dependency(PayrollService)

@router.post(
    "",
    response_model=PayrollResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission([PermissionCode.PAYROLL_CREATE]))]
)
async def create(data: PayrollCreateSchema,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.create(data)

@router.patch(
    "",
    response_model=PayrollResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission([PermissionCode.PAYROLL_UPDATE]))]
)
async def update(data: PayrollUpdateSchema,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[PayrollResponseSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission([PermissionCode.PAYROLL_READ]))]
)
async def get_all(params: RequestAllObject,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.get_all(params)

@router.get(
    "/{id}",
    response_model=PayrollResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission([PermissionCode.PAYROLL_READ]))]
)
async def get(id: int,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.get(id)

@router.delete(
    "/{id}",
    status_code = 204,
    dependencies=[Depends(require_permission([PermissionCode.PAYROLL_DELETE]))]
)
async def delete(id: int,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.delete(id)

@router.post(
    "/cancel",
    status_code = 200,
    response_model = PayrollResponseSchema,
    dependencies=[Depends(require_permission([PermissionCode.PAYROLL_CANCEL]))]
)
async def cancel(id: int,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.cancel(id)