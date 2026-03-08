from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.templates import templates
from app.schemas.user import UserCreate
from app.services.user import sign_up_service


router = APIRouter()


@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("pages/signup.html", {"request": request})


@router.post("/signup")
async def signup_submit(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    first_name: str = Form(...),
    last_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "pages/signup.html",
            {"request": request, "error": "Password does not match"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = UserCreate(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password,
    )

    await sign_up_service(user, db)
    return RedirectResponse("/signin", status_code=status.HTTP_303_SEE_OTHER)
