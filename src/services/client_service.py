import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.client.client_model import Client
from src.schemas.base import PaginationSchema, RequestAllObject
from src.schemas.client.create import ClientCreateSchema
from src.schemas.client.update import ClientDepositUpdateSchema, ClientUpdateSchema, DepositOperation

class ClientService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def create(self, data: ClientCreateSchema) -> Client:
        clientData = data.model_dump()
        newObject = Client(**clientData)
        return await self.uow.clients.create(newObject)

    @require_exists("clients")
    async def update(self, data: ClientUpdateSchema) -> Client:
        return await self.uow.clients.update(data)
    
    async def get(self, id: int) -> Client:
        result = await self.uow.clients.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Client with id {id} not found"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[Client]:
        return await self.uow.clients.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.clients.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    @require_exists("clients")
    async def delete(self, id: int) -> bool:
        return await self.uow.clients.delete(id)
    
    async def updateDeposit(self, data: ClientDepositUpdateSchema) -> Client:
        client = await self.uow.clients.get(data.id)
        if not client:
            raise HTTPException(
                status_code = status.HTTP_404_BAD_REQUEST,
                detail = f"Client with id {data.client_id} not found"
            )
        
        if data.operation not in DepositOperation:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Operation has to be 1 (increment) or -1 (decrement)"
            )
        
        newDeposit = client.deposit + (data.operation * data.amount)
        if newDeposit < 0:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Deposit cannot be negative"
            )
        
        return await self.uow.clients.updateDeposit(client, newDeposit)
    
    @require_exists("clients")
    async def get_appointments(self, data: PaginationSchema, id: int) -> dict:
        items, total_items = await self.uow.appointments.get_by_client(data, id)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }