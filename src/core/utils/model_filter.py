from typing import Any, Type, TypeVar
from sqlalchemy import Select, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=Type[DeclarativeBase])

def apply_dynamic_filters(stmt: Select, model: ModelT, filters: dict[str, Any] | None) -> Select:
    if not filters:
        return stmt

    allowed_fields = getattr(model, "ALLOWED_FILTERS", set())
    filter_clauses = []

    for field_name, value in filters.items():
        if field_name not in allowed_fields or value is None:
            continue

        column = getattr(model, field_name)
        col_type = column.property.columns[0].type

        if isinstance(col_type, SQLEnum) and isinstance(value, str):
            enum_class = col_type.enum_class
            if enum_class is not None:
                try:
                    value = enum_class(value)
                except ValueError:
                    raise ValueError(f"Invalid value '{value}' for enum {enum_class.__name__}")
            filter_clauses.append(column == value)

        elif isinstance(value, str):
            filter_clauses.append(column.ilike(f"%{value}%"))

        else:
            filter_clauses.append(column == value)

    if filter_clauses:
        stmt = stmt.where(*filter_clauses)

    return stmt