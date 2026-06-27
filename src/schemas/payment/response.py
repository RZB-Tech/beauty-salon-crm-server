from pydantic import ConfigDict

from src.repository.payment.payment_model import PaymentMethodsEnum, ReceiptStatus, ReceiptType
from src.schemas.base import BaseResponseSchema

class ReceiptItemResponseSchema(BaseResponseSchema):
    material_id: int | None = None
    appointment_service_id: int | None = None
    price: int
    quantity: int
    notes: str | None = None
    subtotal: int

    model_config = ConfigDict(from_attributes = True)

class ReceiptResponseSchema(BaseResponseSchema):
    receipt_type: ReceiptType
    appointment_id: int | None
    client_id: int | None
    items: list[ReceiptItemResponseSchema]
    total_amount: int

    paid_amount: int
    remaining_amount: int
    status: ReceiptStatus
    change_amount: int = 0
    change_to_deposit: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class PaymentResponseSchema(BaseResponseSchema):
    receipt_id: int
    amount: int
    method: PaymentMethodsEnum

    model_config = ConfigDict(from_attributes = True)