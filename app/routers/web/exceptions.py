from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.core.templates import templates


async def starlette_http_exception_handler(
    request: Request, exc: Exception
) -> Response:
    assert isinstance(exc, StarletteHTTPException)

    # API routes -> JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Web routes -> HTML
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "pages/error.html",
            {"request": request, "user": None, "error": None},
            status_code=404,
        )

    # Fallback for other HTTP errors (optional)
    return templates.TemplateResponse(
        "pages/error.html",
        {"request": request, "user": None, "error": str(exc.detail)},
        status_code=exc.status_code,
    )
