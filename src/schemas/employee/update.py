from decimal import Decimal
from typing import Annotated, Self
from src.schemas.base import BaseUpdateSchema
from pydantic import Field, model_validator
from datetime import date

class EmployeeUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    firstname: str | None = None
    lastname: str | None = None
    middlename: str | None = None
    phone: str | None = None
    birth_date: date | None = None
    specialization_id: int | None = Field(None, ge = 1)
    services: list[Annotated[int, Field(ge = 1)]] | None = None
    salary_fixed: Decimal | None = Field(None, ge = 0,
                                            decimal_places = 2, max_digits = 30) 
    percent_from_services: Decimal | None = Field(None, ge = 0, le = 100,
                                            decimal_places = 2, max_digits = 5)
    percent_from_sales: Decimal | None = Field(None, ge = 0, le = 100,
                                            decimal_places = 2, max_digits = 5)
    notes: str | None = None
    active: bool | None = None
    archived: bool | None = None