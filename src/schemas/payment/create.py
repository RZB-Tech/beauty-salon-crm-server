from typing import Self

from pydantic import BaseModel, Field, model_validator

from src.repository.payment.payment_model import PaymentMethodsEnum, ReceiptType

class ReceiptItemCreateSchema(BaseModel):
    material_id: int = Field(ge=1)
    quantity: int = Field(default=1, ge=1)

class PaymentCreateSchema(BaseModel):
    receipt_id: int = Field(ge = 1)
    amount: int = Field(ge = 1)
    method: PaymentMethodsEnum
    add_change_to_deposit: bool = False

class ReceiptCreateSchema(BaseModel):
    receipt_type: ReceiptType = ReceiptType.APPOINTMENT
    appointment_id: int | None = Field(None, ge = 1)
    client_id: int | None = Field(None, ge = 1)
    receipt_items: list[ReceiptItemCreateSchema] | None = None

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> "ReceiptCreateSchema":
        has_appointment = self.appointment_id is not None
        has_client = self.client_id is not None
        has_items = bool(self.receipt_items)

        if has_appointment and has_items:
            raise ValueError(
                "A receipt cannot be linked to an appointment and contain direct material items simultaneously."
            )
        
        if has_appointment and has_client:
            raise ValueError(
                "A receipt cannot be linked to an appointment and contain client"
            )
        
        if not has_appointment and not has_items:
            raise ValueError(
                "A receipt must contain either an appointment_id or a list of receipt_items."
            )

        if has_appointment and self.receipt_type != ReceiptType.APPOINTMENT:
            raise ValueError("receipt_type must be 'APPOINTMENT' when providing an appointment_id.")
            
        return self