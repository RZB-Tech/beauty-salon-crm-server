from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.database.base import ActorType

T = TypeVar("T")

class PaginatedResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    page: int
    pageSize: int
    totalItems: int
    totalPages: int

class PaginationSchema(BaseModel):
    page: int = Field(
        default=1, 
        ge=1,
        description="Page number (starts at 1)"
    )
    pageSize: int = Field(
        default=10, 
        ge=1, 
        le=100, 
        description="Items per page (max 100)"
    )

class RequestAllObject(PaginationSchema):
    filters: dict[str, Any] | None = {
        "archived": False
    }

class ActorResponseSchema(BaseModel):
    id: int
    display_name: str
    actor_type: ActorType

    model_config = ConfigDict(from_attributes = True)

class BaseResponseSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: ActorResponseSchema | None = None
    archived: bool

class BaseUpdateSchema(BaseModel):
    _exclude_fields: ClassVar[set[str]] = {"id"}
    archived: bool | None = None
    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "BaseUpdateSchema":
        update_fields = {
            field_name for field_name in self.__class__.model_fields 
            if field_name not in self._exclude_fields
        }
        
        if all(getattr(self, field_name) is None for field_name in update_fields):
            readable_fields = ", ".join(f"'{f}'" for f in sorted(update_fields))
            raise ValueError(
                f"At least one of the following fields must be provided: {readable_fields}"
            )
            
        return self
    
class FilterTables(Enum):
    appointments = "appointments"
    clients = "clients"
    employees = "employees"
    employee_absences = "employee_absences"
    employee_work_schedules = "employee_work_schedules"
    materials = "materials"
    payments = "payments"
    payrolls = "payrolls"
    transactions = "transactions"
    receipts = "receipts"
    service_categories = "service_categories"
    services = "services"
    specializations = "specializations"
    notifications = "notifications"
    
class FilterFieldSchema(BaseModel):
    field: str
    type: str
    options: list[str] | None = None