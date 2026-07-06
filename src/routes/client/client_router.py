from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import  make_service_dependency
from src.schemas.appointment.response import AppointmentResponseSchema
from src.schemas.base import PaginatedResponseSchema, PaginationSchema, RequestAllObject
from src.schemas.client.create import ClientCreateSchema
from src.schemas.client.response import ClientResponseSchema
from src.schemas.client.update import ClientDepositUpdateSchema, ClientUpdateSchema
from src.services.client.client_service import ClientService

router = APIRouter()

get_client_service = make_service_dependency(ClientService)

@router.post(
    "", 
    response_model=ClientResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: ClientCreateSchema,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.create(data)

@router.patch(
    "",
    response_model=ClientResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def update(data: ClientUpdateSchema,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ClientResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_all(params: RequestAllObject,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.get_all(params)

@router.get(
    "/{id}",
    response_model=ClientResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def get(id: int,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.get(id)

# @router.delete(
#     "/{id}",
#     status_code = status.HTTP_204_NO_CONTENT
# )
# async def delete(id: int,
#                  clientService: ClientService = Depends(get_client_service)):
#     return await clientService.delete(id)

@router.post(
    "/update-deposit",
    status_code = status.HTTP_200_OK,
    response_model = ClientResponseSchema,
    description = "Для добавления суммы: operaion: 1\nДля отнятия суммы: operataion: -1",
    name = "Обновить депозит"
)
async def update_deposit(data: ClientDepositUpdateSchema,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.updateDeposit(data)

@router.get(
    "/{id}/appointments",
    status_code = status.HTTP_200_OK,
    response_model=PaginatedResponseSchema[AppointmentResponseSchema]
)
async def get_appointments(id: int,
                           params: PaginationSchema = Depends(),
                           clientService: ClientService = Depends(get_client_service)):
    return await clientService.get_appointments(params, id)