from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError

from src.exceptions.base import BaseAppException

# async def sqlalchemy_integrity_exception_handler(request: Request, exc: IntegrityError):
#     error_msg = str(exc.orig).lower() if exc.orig else ""
    
#     if "unique constraint" in error_msg or "duplicate key" in error_msg:
#         raise BaseAppException(
#             detail = "Record with unique value already exists",
#             errorCode = "RECORD_UNIQUE_VALUE_VIOLANCE",
#             statusCode = 409
#         )

#     if "foreign key constraint" in error_msg:
#         raise BaseAppException(
#             detail = "Foreign key not found",
#             errorCode = "FOREIGN_KEY_NOT_FOUND",
#             statusCode = 404
#         )

#     raise BaseAppException(
#         detail = "Database integrity violance",
#         errorCode = "DATABASE_INTEGRITY_VIOLANCE",
#         statusCode = 409
#     )

async def sqlalchemy_integrity_exception_handler(
    request: Request,
    exc: IntegrityError,
):
    orig = exc.orig

    pgcode = getattr(orig, "pgcode", None)
    diag = getattr(orig, "diag", None)

    constraint_name = getattr(diag, "constraint_name", None)

    if pgcode == "23505":
        raise BaseAppException(
            detail="Record with unique value already exists",
            errorCode="RECORD_UNIQUE_VALUE_VIOLATION",
            statusCode=409,
        )

    if pgcode == "23503":
        raise BaseAppException(
            detail="Foreign key not found",
            errorCode="FOREIGN_KEY_NOT_FOUND",
            statusCode=404,
        )

    if pgcode == "23502":
        raise BaseAppException(
            detail="Required database field is missing",
            errorCode="DATABASE_NOT_NULL_VIOLATION",
            statusCode=409,
        )

    if pgcode == "23514":
        raise BaseAppException(
            detail="Database check constraint violated",
            errorCode="DATABASE_CHECK_VIOLATION",
            statusCode=409,
        )

    # Don't hide this during development
    print(
        "Unhandled IntegrityError:",
        {
            "pgcode": pgcode,
            "constraint": constraint_name,
            "orig": repr(orig),
        },
    )

    raise BaseAppException(
        detail="Database integrity violation",
        errorCode="DATABASE_INTEGRITY_VIOLATION",
        statusCode=409,
    )

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(IntegrityError, sqlalchemy_integrity_exception_handler)