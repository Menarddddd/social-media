from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.web_dep import require_user_web
from app.models.post import Post
from app.models.user import User
from app.repositories.post import get_post_by_id_db, delete_post_db
from app.schemas.post import PostUpdate
from app.services.post import update_post_service

router = APIRouter()


async def post_owner_web(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_user_web)],
) -> Post:
    post = await get_post_by_id_db(post_id, db)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return post


@router.post("/posts/{post_id}/edit")
async def edit_post_web(
    post: Annotated[Post, Depends(post_owner_web)],
    db: Annotated[AsyncSession, Depends(get_db)],
    title: Annotated[str, Form(...)],
    content: Annotated[str, Form(...)],
    next: Annotated[str, Form()] = "/profile",
):
    form_data = PostUpdate(title=title, content=content)
    await update_post_service(form_data, post, db)

    if not next.startswith("/"):
        next = "/profile"

    return RedirectResponse(next, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/posts/{post_id}/delete")
async def delete_post_web(
    post: Annotated[Post, Depends(post_owner_web)],
    db: Annotated[AsyncSession, Depends(get_db)],
    next: Annotated[str, Form()] = "/profile",
):
    await delete_post_db(post, db)

    if not next.startswith("/"):
        next = "/profile"

    return RedirectResponse(next, status_code=status.HTTP_303_SEE_OTHER)
