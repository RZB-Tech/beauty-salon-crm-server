# src/core/exceptions.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

async def sqlalchemy_integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    error_msg = str(exc.orig).lower() if exc.orig else ""
    
    if "unique constraint" in error_msg or "duplicate key" in error_msg:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "A record with this unique value already exists."}
        )
        
    if "foreign key constraint" in error_msg:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Referenced related record does not exist."}
        )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity validation failed."}
    )

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(IntegrityError, sqlalchemy_integrity_exception_handler)