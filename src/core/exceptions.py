from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError

from src.exceptions.base import BaseAppException

async def sqlalchemy_integrity_exception_handler(request: Request, exc: IntegrityError):
    error_msg = str(exc.orig).lower() if exc.orig else ""
    
    if "unique constraint" in error_msg or "duplicate key" in error_msg:
        raise BaseAppException(
            detail = "Record with unique value already exists",
            errorCode = "RECORD_UNIQUE_VALUE_VIOLANCE",
            statusCode = 409
        )

    if "foreign key constraint" in error_msg:
        raise BaseAppException(
            detail = "Foreign key not found",
            errorCode = "FOREIGN_KEY_NOT_FOUND",
            statusCode = 404
        )

    raise BaseAppException(
        detail = "Database integrity violance",
        errorCode = "DATABASE_INTEGRITY_VIOLANCE",
        statusCode = 409
    )

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(IntegrityError, sqlalchemy_integrity_exception_handler)