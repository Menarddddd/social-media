from typing import Annotated, List
from uuid import UUID

from fastapi import Depends, Query, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import get_current_user, post_owner
from app.models.post import Post
from app.models.user import User
from app.repositories.post import delete_post_db
from app.schemas.post import (
    PostCreate,
    PostFeedResponse,
    PostResponse,
    PostUpdate,
    PostWithCommentAuthorResponse,
)
from app.services.post import (
    create_post_service,
    feed_post_service,
    get_post_service,
    my_posts_service,
    update_post_service,
)


router = APIRouter()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    form_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_post_service(form_data, db, current_user)


@router.get(
    "/feed", response_model=List[PostFeedResponse], status_code=status.HTTP_200_OK
)
async def feed(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    return await feed_post_service(db, page, limit)


@router.get(
    "",
    response_model=List[PostWithCommentAuthorResponse],
    status_code=status.HTTP_200_OK,
)
async def my_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    return await my_posts_service(db, current_user, page, limit)


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_post_service(post_id, db)


@router.patch("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def update_post(
    form_data: PostUpdate,
    post: Annotated[Post, Depends(post_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await update_post_service(form_data, post, db)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: Annotated[Post, Depends(post_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await delete_post_db(post, db)
