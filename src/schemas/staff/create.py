from pydantic import BaseModel, Field

class StaffCreateBaseSchema(BaseModel):
    firstname: str = Field(..., max_length=255)
    lastname: str | None = Field(None, max_length=255)
    middlename: str | None = Field(None, max_length=255)
    login: str = Field(max_length = 100)
    employee_id: int | None = Field(None, ge = 1)
    active: bool | None = None

class StaffCreateAPISchema(StaffCreateBaseSchema):
    password: str = Field(max_length = 255)

class StaffCreateDBSchema(StaffCreateBaseSchema):
    hashed_password: str = Field(max_length = 255)