from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import  make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payroll.create import PayrollCreateSchema
from src.schemas.payroll.response import PayrollResponseSchema
from src.schemas.payroll.update import PayrollUpdateSchema
from src.services.payroll_service import PayrollService

router = APIRouter()

get_payroll_service = make_service_dependency(PayrollService)

@router.post(
    "/", 
    response_model=PayrollResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: PayrollCreateSchema,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.create(data)

@router.patch(
    "/",
    response_model=PayrollResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def update(data: PayrollUpdateSchema,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[PayrollResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_all(params: RequestAllObject,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.get_all(params)

@router.get(
    "/{id}",
    response_model=PayrollResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def get(id: int,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.get(id)

@router.delete(
    "/{id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete(id: int,
                 payrollService: PayrollService = Depends(get_payroll_service)):
    return await payrollService.delete(id)