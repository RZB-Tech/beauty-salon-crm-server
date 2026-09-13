from pydantic import ConfigDict
from src.repository.receipt.receipt_model import ReceiptStatus, ReceiptType
from src.repository.transaction.transaction_model import TransactionMethod
from src.schemas.base import BaseResponseSchema, MoneyResponse

class ReceiptItemResponseSchema(BaseResponseSchema):
    material_id: int | None = None
    appointment_service_id: int | None = None
    base_price: MoneyResponse
    final_price: MoneyResponse
    quantity: int
    discount_amount: MoneyResponse
    notes: str | None = None
    total_price: MoneyResponse

    model_config = ConfigDict(from_attributes = True)

class ReceiptResponseSchema(BaseResponseSchema):
    receipt_type: ReceiptType
    appointment_id: int | None
    client_id: int | None
    items: list[ReceiptItemResponseSchema]
    subtotal_amount: MoneyResponse
    total_amount: MoneyResponse
    discount_amount: MoneyResponse

    paid_amount: MoneyResponse
    remaining_amount: MoneyResponse
    status: ReceiptStatus
    change_amount: MoneyResponse
    change_to_deposit: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class PaymentResponseSchema(BaseResponseSchema):
    receipt_id: int
    amount: MoneyResponse
    method: TransactionMethod

    model_config = ConfigDict(from_attributes = True)