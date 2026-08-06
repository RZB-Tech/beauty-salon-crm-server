from typing import Annotated, Self
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
                raise ValueError("Date period and list of payrolls can be specified in one request, only of them per request")
            
            if bool(self.start_date) != bool(self.end_date):
                raise ValueError("Required to specify start_date and end_date, or do not specify date period at all")
            
            if (self.start_date and self.end_date) and (self.start_date > self.end_date):
                raise ValueError("End time of date period cannot be earlier than stat time")
        
        elif self.type in {PayoutType.SALARY, PayoutType.ADVANCE_SALARY}:
            if self.amount and self.type == PayoutType.SALARY:
                raise ValueError("In payout type 'salary' cannot manually provide amount, only in 'advance_salary")
            
            if self.payrolls:
                raise ValueError("When 'salary' or 'advance_salary' provided in type, restricted to provide payrolls")

            if self.start_date or self.end_date:
                raise ValueError("Restricted to provide period for type 'salary' and 'advance_salary'")

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