from typing import Any, Type, TypeVar
from sqlalchemy import Select, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase
from datetime import date, datetime

ModelT = TypeVar("ModelT", bound=Type[DeclarativeBase])

_OPERATORS = {
    "eq": lambda col, val: col == val,
    "ne": lambda col, val: col != val,
    "gt": lambda col, val: col > val,
    "gte": lambda col, val: col >= val,
    "lt": lambda col, val: col < val,
    "lte": lambda col, val: col <= val,
}

def _coerce_value(col_type, value: Any) -> Any:
    py_type = col_type.python_type
    if isinstance(value, str):
        if py_type is date:
            return date.fromisoformat(value)
        if py_type is datetime:
            return datetime.fromisoformat(value)
        if py_type in (int, float):
            return py_type(value)
        if py_type is bool:
            return value.lower() in ("1", "true", "yes")
    return value


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

        # Enum fields: unchanged, equality only
        if isinstance(col_type, SQLEnum):
            enum_class = col_type.enum_class
            if isinstance(value, str) and enum_class is not None:
                try:
                    value = enum_class(value)
                except ValueError:
                    raise ValueError(f"Invalid value '{value}' for enum {enum_class.__name__}")
            filter_clauses.append(column == value)
            continue

        # Operator dict: {"gte": ..., "lte": ...}
        if isinstance(value, dict):
            for op, op_value in value.items():
                if op not in _OPERATORS:
                    raise ValueError(f"Unsupported operator '{op}' for field '{field_name}'")
                coerced = _coerce_value(col_type, op_value)
                filter_clauses.append(_OPERATORS[op](column, coerced))
            continue

        # Plain string on a text column: partial match
        if col_type.python_type is str and isinstance(value, str):
            filter_clauses.append(column.ilike(f"%{value}%"))
            continue

        # Everything else: coerce + equality
        coerced = _coerce_value(col_type, value)
        filter_clauses.append(column == coerced)

    if filter_clauses:
        stmt = stmt.where(*filter_clauses)

    return stmt