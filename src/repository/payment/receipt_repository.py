from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords
from src.repository.payment.payment_model import Receipt, ReceiptItem
from src.schemas.base import RequestAllObject
from src.schemas.payment.create import ReceiptCreateSchema

class ReceiptRepository(BaseRepository):
    async def create(self, receipt: Receipt) -> Receipt | None:
        self.db.add(receipt)
        await self.db.flush()

        stmt = (
            select(Receipt)
            .where(Receipt.id == receipt.id)
            .options(
                selectinload(Receipt.items),
                selectinload(Receipt.payments)
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

        # stmt = (
        #     select(Appointment)
        #     .where(Appointment.id == receipt.appointment_id)
        #     .options(
        #         selectinload(Appointment.records)
        #         .selectinload(AppointmentRecords.services)
        #     )
        # )
        # result = await self.db.execute(stmt)
        # appointment = result.scalar_one_or_none()

        # if not appointment:
        #     raise ValueError(f"Appointment with id {receipt.appointment_id} not found.")

        # total = 0
        # receipt_items = []
        
        # for record in appointment.records:
        #     for service in record.services:
        #         item = ReceiptItem(
        #             appointment_service_id=service.id,
        #             price=service.price,
        #             quantity=service.quantity
        #         )
        #         total += (service.price * service.quantity)
        #         receipt_items.append(item)
                
        # receipt.total_amount = total
        # receipt.items = receipt_items 

        # self.db.add(receipt)
        # await self.db.commit()
        
        # final_stmt = (
        #     select(Receipt)
        #     .where(Receipt.id == receipt.id)
        #     .options(
        #         selectinload(Receipt.items),
        #         selectinload(Receipt.payments) # 🌟 Bakes in payments so paid_amount doesn't trigger lazy loading
        #     )
        # )
        # final_result = await self.db.execute(final_stmt)
        # return final_result.scalar_one()
    
    # async def get_by_ids(self, ids: list[int]) -> list[Receipt]:
    #     result = await self.db.execute(
    #         select(Receipt).where(Receipt.id.in_(ids))
    #     )
    #     return list(result.scalars().all())
    
    async def get(self, id: int) -> Receipt:
        result = await self.db.execute(
            select(Receipt)
            .where(Receipt.id == id)
            .options(
                selectinload(Receipt.items),
                selectinload(Receipt.payments),
                selectinload(Receipt.appointment)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Receipt], int]:
        count_stmt = select(func.count()).select_from(Receipt)
        stmt = select(Receipt)
        count_stmt = apply_dynamic_filters(count_stmt, Receipt, data.filters)
        stmt = apply_dynamic_filters(stmt, Receipt, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (stmt
                .options(
                    selectinload(Receipt.items),
                    selectinload(Receipt.payments))
                .order_by(Receipt.id.desc())
                .offset(offset_value)
                .limit(data.pageSize))
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    # async def update(self, payload: PayrollUpdateSchema) -> Payroll | None:
    #     obj = await self.db.get(Payroll, payload.id)
    #     if not obj:
    #         return None

    #     update_data = payload.model_dump(exclude_unset=True)

    #     update_data.pop("id", None)

    #     for field, value in update_data.items():
    #         setattr(obj, field, value)

    #     await self.db.commit()
    #     await self.db.refresh(obj)

    #     return obj
    
    # async def delete(self, id: int) -> bool:
    #     obj = await self.db.get(Payroll, id)
    #     if not obj:
    #         return False

    #     await self.db.delete(obj)
    #     await self.db.commit()
    #     return True
    
    # async def get_by_employee(self, id: int) -> list[Payroll] | None:
    #     result =  await self.db.execute(
    #         select(Payroll)
    #         .where(Payroll.employee_id == id)
    #     )
    #     return result.scalars().all()