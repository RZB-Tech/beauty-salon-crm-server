import math
from fastapi import UploadFile
from sqlalchemy import select
from src.core.dependencies.context import get_current_actor_id, get_current_staff_id, get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.auth_exceptions import AuthTenantContextEmpty
from src.exceptions.base import BaseAppException
from src.exceptions.category_exceptions import ServiceCategoryIsArchived, ServiceCategoryNotFound
from src.exceptions.service_exceptions import ServiceNotFound
from src.repository.service.service_model import Service, ServiceCategory
from src.schemas.analytics.request import GetReportWithFilters
from src.schemas.analytics.serviceResponse import ServiceAnalyticsBaseResponse, ServiceAnalyticsResponse
from src.schemas.base import RequestAllObject
from src.schemas.service.create import ServiceCreateSchema
from src.schemas.service.update import ServiceUpdateSchema
from src.database.session import db_session_ctx
from io import BytesIO
import pandas as pd

class ServiceService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, serviceIn: ServiceCreateSchema) -> Service:
        serviceData = serviceIn.model_dump()
        newService = Service(**serviceData)
        return await self.uow.services.create(newService)

    async def update(self, data: ServiceUpdateSchema) -> Service:
        service = await self.uow.services.get_with_employees(data.id)
        if service is None: raise ServiceNotFound(data.id)

        if data.category_id:
            checkCategory = await self.uow.serviceCategory.get(data.category_id)
            if checkCategory is None: raise ServiceCategoryNotFound(data.category_id)
            if checkCategory.archived: raise ServiceCategoryIsArchived(data.category_id, checkCategory.name)

        if data.archived: service.employees.clear()

        dataDict = data.model_dump(exclude = {"id"}, exclude_unset = True)
        result = await self.uow.services.update(data.id, **dataDict)

        if result is None: raise ServiceNotFound(data.id)
        return result
    
    async def get(self, id: int) -> Service:
        result = await self.uow.services.get(id)
        if not result: raise ServiceNotFound(id)
        return result
    
    async def get_many(self, ids: list[int]) -> list[Service]:
        return await self.uow.services.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.services.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def delete(self, id: int) -> bool:
        return await self.uow.services.delete(id)

    async def import_excel(
        self, 
        file: UploadFile,
    ) -> dict:
        db = db_session_ctx.get()
        file_bytes = await file.read()
        df = pd.read_excel(BytesIO(file_bytes))
        required_columns = {
            "service_category",
            "service",
            "price"
        }

        if not required_columns.issubset(df.columns):
            raise BaseAppException(
                detail = f"Excel has to contain columns: {required_columns}",
                errorCode = "EXCEL_DOES_NOT_CONTAIN_REQUIRED_COLUMNS",
                statusCode = 400,
                required_columns = list(required_columns)
            )
        
        tenant_id = get_current_tenant_id()
        staff_id = get_current_staff_id()
        actor_id = get_current_actor_id()

        if tenant_id is None or staff_id is None: raise AuthTenantContextEmpty()

        df = df.dropna(subset=["service"])
        category_names = (
            df["service_category"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
        
        result = await db.execute(
            select(ServiceCategory).where(
                ServiceCategory.name.in_(category_names)
            )
        )

        existing_categories = {
            category.name: category
            for category in result.scalars().all()
        }

        new_categories = []

        for category_name in category_names:
            if category_name not in existing_categories:
                category = ServiceCategory(
                    name=category_name,
                    created_by_actor_id = actor_id,
                    tenant_id = tenant_id
                )
                db.add(category)
                new_categories.append(category)
                existing_categories[category_name] = category

        if new_categories:
            await db.flush()

        result = await db.execute(
            select(Service.name)
        )

        existing_service_names = set(result.scalars().all())

        created_services = 0

        for _, row in df.iterrows():
            service_name = str(row["service"]).strip()

            if service_name in existing_service_names:
                continue

            category_name = str(
                row["service_category"]
            ).strip()

            category = existing_categories[category_name]

            price = row["price"]
            estm = row["estimated_time"]
            service = Service(
                name=service_name,
                price=0 if pd.isna(price) else int(price),
                estimated_time = 0 if pd.isna(estm) else int(estm),
                category_id=category.id,
                created_by_actor_id = actor_id,
                tenant_id = tenant_id
            )

            db.add(service)

            created_services += 1
            existing_service_names.add(service_name)

        await db.commit()

        return {
            "created_categories": len(new_categories),
            "created_services": created_services,
        }

    async def get_analytics(self, data: GetReportWithFilters) -> ServiceAnalyticsResponse:
        rows = await self.uow.services.get_analytics(data)
        return ServiceAnalyticsResponse(
            items = [
                ServiceAnalyticsBaseResponse(
                    service_id = row.service_id,
                    service_name = row.name,
                    amount = row.amount,
                    revenue = row.revenue
                )
                for row in rows
            ]
        )
