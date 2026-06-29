from typing import Annotated, Self

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator

from src.repository.payroll.payroll_model import PayoutMethod, PayoutType
from datetime import date

class PayoutCreateSchema(BaseModel):
    employee_id: int = Field(..., ge = 1)
    type: PayoutType
    method: PayoutMethod
    notes: str | None = None
    payrolls: list[Annotated[int, Field(ge = 1)]] | None = Field(None, min_length = 1)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode = "after")
    def check(self) -> Self:
        if self.payrolls and (self.start_date or self.end_date):
            raise HTTPException(400, "Нельзя указывать период времени и список выплат, только один из двух")
        
        if bool(self.start_date) != bool(self.end_date):
            raise HTTPException(400, "Необходимо указать как начало, так и конец периода, либо не указывать их вообще")
        
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise HTTPException(400, "Начало не может быть позже конца периода")
        
        return self