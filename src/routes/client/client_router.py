from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.appointment.response import AppointmentResponseSchema
from src.schemas.base import PaginatedResponseSchema, PaginationSchema, RequestAllObject
from src.schemas.client.create import ClientCreateSchema
from src.schemas.client.request import ClientFinanceReportRequest
from src.schemas.client.response import ClientFinanceResponseSchema, ClientResponseSchema
from src.schemas.client.update import ClientDepositUpdateSchema, ClientUpdateSchema
from src.services.client.client_service import ClientService

router = APIRouter()

get_client_service = make_service_dependency(ClientService)

@router.post(
    "",
    response_model=ClientResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового клиента",
    dependencies=[Depends(require_permission([PermissionCode.CLIENT_CREATE]))]
)
async def create(data: ClientCreateSchema,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.create(data)

@router.patch(
    "",
    response_model=ClientResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Обновить клиента",
    description="Обновляет данные клиента по его `id`. Передаются только изменяемые поля.",
    dependencies=[Depends(require_permission([PermissionCode.CLIENT_UPDATE]))]
)
async def update(data: ClientUpdateSchema,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ClientResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Получить всех клиентов",
    description="Возвращает постраничный список клиентов организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.CLIENT_READ]))]
)
async def get_all(params: RequestAllObject,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.get_all(params)

@router.get(
    "/{id}",
    response_model=ClientResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить клиента по ID",
    dependencies=[Depends(require_permission([PermissionCode.CLIENT_READ]))]
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
    summary = "Обновить депозит клиента",
    description = "Изменяет депозит клиента. Для пополнения: `operation: 1`; для списания: `operation: -1`. Итоговый депозит не может стать отрицательным.",
    name = "Обновить депозит",
    dependencies=[Depends(require_permission([PermissionCode.CLIENT_UPDATE_DEPOSIT]))]
)
async def update_deposit(data: ClientDepositUpdateSchema,
                 clientService: ClientService = Depends(get_client_service)):
    return await clientService.updateDeposit(data)

@router.get(
    "/{id}/appointments",
    status_code = status.HTTP_200_OK,
    response_model=PaginatedResponseSchema[AppointmentResponseSchema],
    summary = "Посещения клиента",
    description = "Возвращает постраничный список посещений указанного клиента.",
    dependencies=[Depends(require_permission([PermissionCode.CLIENT_READ]))]
)
async def get_appointments(id: int,
                           params: PaginationSchema = Depends(),
                           clientService: ClientService = Depends(get_client_service)):
    return await clientService.get_appointments(params, id)

@router.post(
    "/finance-report",
    status_code = 200,
    response_model = ClientFinanceResponseSchema,
    summary = "Финансовый отчет по клиенту",
    description = """
Запрос на получение финансового отчета по клиенту. В теле запроса указывается `clientID`, `start_date` и `end_date` (оба поля опциональны).

Если по клиенту нету никаких отчетов - возращает "items": {}.

Если по клиенту есть отчеты - возвращает:
```json
"items": {
    "yyyy-mm": {
        "income": integer (общий доход)
        "expense": integer (общий расход)
        "net": integer (income - expense)
        "transactions": [Transaction]
    },
    "yyyy-mm": {
        ...
    },
}
```
""",
    dependencies=[Depends(require_permission([PermissionCode.CLIENT_FINANCE_REPORT]))]
)
async def get_finance_report(data: ClientFinanceReportRequest,
                             clientService: ClientService = Depends(get_client_service)):
    return await clientService.get_finance_report(data)
