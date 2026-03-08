from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.web_dep import require_user_web
from app.models.user import User
from app.schemas.post import PostCreate
from app.services.post import create_post_service

router = APIRouter()


@router.post("/posts")
async def create_post_web(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_user_web)],
    title: Annotated[str, Form(...)],
    content: Annotated[str, Form(...)],
    next: Annotated[str, Form()] = "/feed",
):
    post_data = PostCreate(title=title, content=content)
    await create_post_service(post_data, db, current_user)

    if not next.startswith("/"):
        next = "/feed"

    return RedirectResponse(url=next, status_code=status.HTTP_303_SEE_OTHER)
