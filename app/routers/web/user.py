from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.templates import templates
from app.core.web_dep import require_user_web
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.repositories.user import get_active_user_by_id_db

router = APIRouter()


@router.get("/users/{user_id}", response_class=HTMLResponse)
async def user_profile_page(
    request: Request,
    user_id: UUID,
    current_user: Annotated[User, Depends(require_user_web)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    profile_user = await get_active_user_by_id_db(
        user_id,
        db,
        selectinload(User.posts)
        .selectinload(Post.comments)
        .selectinload(Comment.author),
    )

    if profile_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return templates.TemplateResponse(
        "pages/user_profile.html",
        {
            "request": request,
            "user": current_user,  # for navbar auth
            "profile_user": profile_user,  # the profile being viewed
        },
    )
