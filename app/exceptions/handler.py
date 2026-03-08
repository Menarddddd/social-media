from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core import templates
from app.exceptions.exception import (
    DuplicateEntryException,
    FieldNotFoundException,
    InvalidCredentialsError,
)


async def invalid_credentials_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    assert isinstance(exc, InvalidCredentialsError)

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def field_not_found_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, FieldNotFoundException)

    return JSONResponse(
        content={f"{exc.field}": f"{exc.value}", "message": str(exc)},
    )


async def duplicate_entry_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, DuplicateEntryException)

    return JSONResponse(
        status_code=409,
        content={exc.field: exc.value, "message": str(exc)},
    )
