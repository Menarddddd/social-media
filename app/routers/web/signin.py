from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.templates import templates
from app.exceptions.exception import InvalidCredentialsError
from app.services.user import sign_in_service


router = APIRouter()


@router.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    error = request.query_params.get("error")
    error = "Invalid credentials" if error == "1" else None

    return templates.TemplateResponse(
        "pages/signin.html",
        {"request": request, "error": error},
    )


@router.post("/signin")
async def signin_submit(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    username: str = Form(...),
    password: str = Form(...),
):
    try:
        token_data = await sign_in_service(username, password, db)
    except InvalidCredentialsError:
        return RedirectResponse(url="/signin?error=1", status_code=303)

    resp = RedirectResponse(url="/feed", status_code=303)

    resp.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=30 * 30,
        path="/",
    )

    return resp
