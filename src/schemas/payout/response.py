from typing import Annotated, Self

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.repository.payroll.payroll_model import PayoutType
from datetime import date

from src.schemas.payroll.response import PayrollResponseSchema

class PayoutResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    employee_id: int
    type: PayoutType
    notes: str | None = None
    payrolls: list[PayrollResponseSchema] = Field(default_factory = list)
    total_amount: int