from pydantic import ConfigDict
from src.repository.receipt.receipt_model import ReceiptStatus, ReceiptType
from src.repository.transaction.transaction_model import TransactionMethod
from src.schemas.base import BaseResponseSchema

class ReceiptItemResponseSchema(BaseResponseSchema):
    material_id: int | None = None
    appointment_service_id: int | None = None
    base_price: int
    final_price: int
    quantity: int
    discount_amount: int
    notes: str | None = None
    total_price: int

    model_config = ConfigDict(from_attributes = True)

class ReceiptResponseSchema(BaseResponseSchema):
    receipt_type: ReceiptType
    appointment_id: int | None
    client_id: int | None
    items: list[ReceiptItemResponseSchema]
    subtotal_amount: int
    total_amount: int
    discount_amount: int

    paid_amount: int
    remaining_amount: int
    status: ReceiptStatus
    change_amount: int = 0
    change_to_deposit: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class PaymentResponseSchema(BaseResponseSchema):
    receipt_id: int
    amount: int
    method: TransactionMethod

    model_config = ConfigDict(from_attributes = True)