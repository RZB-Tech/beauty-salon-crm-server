from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator

class EmployeeCreateSchema(BaseModel):
    firstname: str = Field(max_length=100, description="Имя сотрудника")
    lastname: str = Field(max_length=100)
    middlename: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    birth_date: date
    active: bool = True
    specialization_id: int | None = None
    services_ids: list[int] = Field(default_factory = list)
    salary_fixed: int | None = Field(None, ge = 0)
    percent_from_services: int | None = Field(None, ge = 0)
    percent_from_sales: int | None = Field(None, ge = 0)

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
            raise ValueError("Employee has to be not younger than 18 years old")

        return birth_date

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "firstname": "Мария",
            "lastname": "Петрова",
            "middlename": "Сергеевна",
            "phone": "+998901234567",
            "birth_date": "1995-05-20",
            "active": True,
            "specialization_id": 1,
            "services_ids": [1, 2],
            "salary_fixed": 3000000,
            "percent_from_services": 15,
            "percent_from_sales": 5
        }
    })