from datetime import datetime
from typing import Any, ClassVar, Generic, TypeVar
from pydantic import BaseModel, Field, field_serializer, model_validator

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
    filters: dict[str, Any] | None = None

class BaseResponseSchema(BaseModel):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int | None
    archived: bool

class BaseUpdateSchema(BaseModel):
    _exclude_fields: ClassVar[set[str]] = {"id"}

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