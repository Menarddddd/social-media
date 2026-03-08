from typing import Annotated, List
from uuid import UUID

from fastapi import Depends, Query, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import comment_owner, get_current_user
from app.models.comment import Comment
from app.models.user import User
from app.repositories.comment import delete_comment_db
from app.schemas.comment import (
    CommentCreate,
    CommentLoadedResponse,
    CommentResponse,
    CommentUpdate,
    CommentWithPostAuthorResponse,
)
from app.services.comment import (
    create_comment_api_service,
    create_comment_service,
    get_comment_service,
    my_comments_service,
    update_comment_service,
)


router = APIRouter()


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    form_data: CommentCreate,
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_comment_api_service(form_data, post_id, db, current_user)


@router.get(
    "",
    response_model=List[CommentWithPostAuthorResponse],
    status_code=status.HTTP_200_OK,
)
async def my_comments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    return await my_comments_service(db, current_user, page, limit)


@router.get(
    "/{comment_id}",
    response_model=CommentLoadedResponse,
    status_code=status.HTTP_200_OK,
)
async def get_comment(
    comment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_comment_service(comment_id, db)


@router.patch(
    "/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK
)
async def update_comment(
    form_data: CommentUpdate,
    comment: Annotated[Comment, Depends(comment_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await update_comment_service(form_data, comment, db)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment: Annotated[Comment, Depends(comment_owner)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await delete_comment_db(comment, db)
