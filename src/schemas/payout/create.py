from typing import Annotated, Self

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.repository.payroll.payroll_model import PayoutMethod, PayoutType
from datetime import date

class PayoutCreateSchema(BaseModel):
    employee_id: int = Field(..., ge = 1)
    type: PayoutType | None = PayoutType.OTHER
    amount: int | None = Field(None, ge = 1)
    method: PayoutMethod | None = PayoutMethod.CASH
    notes: str | None = None
    payrolls: list[Annotated[int, Field(ge = 1)]] | None = Field(None, min_length = 1)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode = "after")
    def check(self) -> Self:
        if self.type == PayoutType.OTHER:
            if self.payrolls and ((self.start_date or self.end_date)):
                raise HTTPException(400, "Нельзя указывать период времени и список выплат, только одно из двух")
            
            if bool(self.start_date) != bool(self.end_date):
                raise HTTPException(400, "Необходимо указать как начало, так и конец периода, либо не указывать их вообще")
            
            if (self.start_date and self.end_date) and (self.start_date > self.end_date):
                raise HTTPException(400, "Начало не может быть позже конца периода")
        
        elif self.type in {PayoutType.SALARY, PayoutType.ADVANCE_SALARY}:
            if self.amount and self.type == PayoutType.SALARY:
                raise HTTPException(400, "Указывать выплачиваемую сумму можно только если категория выплаты - Аванс")
            
            if self.payrolls:
                raise HTTPException(400, "При выбранной категории Заработная плата / Аванс, нельзя указывать выплаты.")

            if self.start_date or self.end_date:
                raise HTTPException(400, "Нельзя указывать период времени для выплаты заработной платы / аванса")

        return self

    model_config = ConfigDict(json_schema_extra = {
        "examples": [
            {
                "employee_id": 1,
                "type": "other",
                "method": "cash",
                "start_date": "2026-07-01",
                "end_date": "2026-07-31"
            },
            {
                "employee_id": 1,
                "type": "advance salary",
                "amount": 1000000,
                "method": "card"
            }
        ]
    })