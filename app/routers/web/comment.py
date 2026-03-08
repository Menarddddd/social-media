from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.web_dep import require_user_web
from app.models.user import User
from app.services.comment import create_comment_service

router = APIRouter()


@router.post("/posts/{post_id}/comments")
async def create_comment_web(
    post_id: UUID,
    message: Annotated[str, Form(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_user_web)],
    next: Annotated[str, Form()] = "/feed",
):
    await create_comment_service(
        message=message,
        post_id=post_id,
        db=db,
        user=current_user,
    )

    if not next.startswith("/"):
        next = "/feed"

    return RedirectResponse(url=next, status_code=status.HTTP_303_SEE_OTHER)
