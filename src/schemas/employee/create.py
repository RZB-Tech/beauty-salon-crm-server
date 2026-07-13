from datetime import date
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator

class EmployeeCreateSchema(BaseModel):
    firstname: str = Field(max_length=100, description="Employee's first name")
    lastname: str = Field(max_length=100)
    middlename: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    birth_date: date
    active: bool = True
    specialization_id: int | None = None
    services_ids: list[int] = Field(default_factory = list)
    salary_fixed: int | None = 0
    percent_from_services: int | None = 0
    percent_from_sales: int | None = 0

    @field_validator("birth_date")
    @classmethod
    def validate_age(cls, birth_date: date) -> date:
        today = date.today()

        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        if age < 18:
            raise HTTPException(400, "Возраст сотрудника должен быть не менее 18 лет.")

        return birth_date