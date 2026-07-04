from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import make_service_dependency
from src.schemas.appointment.response import AppointmentResponseSchema
from src.schemas.base import PaginatedResponseSchema, PaginationSchema, RequestAllObject
from src.schemas.employee.create import EmployeeCreateSchema
from src.schemas.employee.response import EmployeeResponseBase, EmployeeWorkScheduleResponse
from src.schemas.employee.update import EmployeeUpdateSchema
from src.schemas.payroll.response import PayrollResponseSchema
from src.services.employee_service import EmployeeService

router = APIRouter()

get_employee_service = make_service_dependency(EmployeeService)

@router.post(
    "", 
    response_model=EmployeeResponseBase, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee with assigned services"
)
async def create(
    data: EmployeeCreateSchema,
    employeeService: EmployeeService = Depends(get_employee_service)
):
    return await employeeService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[EmployeeResponseBase], 
    status_code=status.HTTP_200_OK
)
async def get_all(params: RequestAllObject,
    employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.get_all(params)

# @router.post(
#     "/get-many",
#     response_model=list[EmployeeResponseBase], 
#     status_code=status.HTTP_200_OK
# )
# async def get_many(data: list[int],
#     employeeService: EmployeeService = Depends(get_employee_service)):
#     return await employeeService.get_many(data)

@router.get(
    "/{id}",
    response_model = EmployeeResponseBase,
    status_code = status.HTTP_200_OK,
)
async def get(id: int,
    employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.get(id)

@router.patch(
    "",
    response_model=EmployeeResponseBase, 
    status_code=status.HTTP_200_OK
)
async def update(data: EmployeeUpdateSchema,
    employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.update(data)

@router.delete(
    "/{id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete(id: int,
    employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.delete(id)

@router.get(
    "/{id}/work-schedules",
    status_code = status.HTTP_200_OK,
    response_model = EmployeeWorkScheduleResponse,
    description = "Returns employee's work schedules and absences"
)
async def get_workSchedules(id: int,
    employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.get_workSchedules(id)

@router.get(
    "/{id}/payrolls",
    status_code = status.HTTP_200_OK,
    response_model = PaginatedResponseSchema[PayrollResponseSchema],
    description = "Returns employee's payrolls"
)
async def get_payrolls(id: int,
                       params: PaginationSchema = Depends(),
                       employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.get_payrolls(params, id)

@router.get(
    "/{id}/appointments",
    status_code = status.HTTP_200_OK,
    response_model=PaginatedResponseSchema[AppointmentResponseSchema]
)
async def get_appointments(id: int,
                           params: PaginationSchema = Depends(),
                           employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.get_appointments(params, id)