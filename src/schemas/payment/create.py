from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.repository.receipt.receipt_model import ReceiptType
from src.repository.transaction.transaction_model import TransactionMethod

class ReceiptItemCreateSchema(BaseModel):
    material_id: int = Field(ge=1)
    quantity: int = Field(default=1, ge=1)

class ReceiptPaymentCreateSchema(BaseModel):
    receipt_id: int = Field(ge = 1)
    amount: int = Field(ge = 1)
    method: TransactionMethod
    add_change_to_deposit: bool = True

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "receipt_id": 1,
            "amount": 150000,
            "method": "cash",
            "add_change_to_deposit": True
        }
    })

class ReceiptCreateSchema(BaseModel):
    receipt_type: ReceiptType = ReceiptType.APPOINTMENT
    appointment_id: int | None = Field(None, ge = 1)
    client_id: int | None = Field(None, ge = 1)
    receipt_items: list[ReceiptItemCreateSchema] | None = None

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> Self:
        has_appointment = self.appointment_id is not None
        has_client = self.client_id is not None
        has_items = bool(self.receipt_items)

        if has_appointment and has_items:
            raise ValueError("Receipt can be have appointment_id and receipt_items on one request")

        if has_appointment and has_client:
            raise ValueError("Receipt cannot have appointment_id and client_id on one request")

        if not has_appointment and not has_items:
            raise ValueError("Required to provide either appointment_id or receipt_items, only one of them")

        if has_appointment and self.receipt_type != ReceiptType.APPOINTMENT:
            raise ValueError("If appointment_id provided - receipt_type has to be 'appointment'") 

        return self

    model_config = ConfigDict(json_schema_extra = {
        "examples": [
            {
                "receipt_type": "appointment",
                "appointment_id": 1
            },
            {
                "receipt_type": "direct sale",
                "client_id": 1,
                "receipt_items": [
                    {"material_id": 1, "quantity": 2}
                ]
            }
        ]
    })