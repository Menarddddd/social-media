from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions.exception import FieldNotFoundException
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.repositories.comment import get_comment_by_id_db, get_user_comments_db
from app.schemas.comment import CommentCreate, CommentUpdate


async def create_comment_api_service(
    form_data: CommentCreate, post_id: UUID, db: AsyncSession, user: User
) -> Comment:
    new_comment = Comment(message=form_data.message, post_id=post_id, author=user)

    db.add(new_comment)
    await db.flush()

    return new_comment


async def create_comment_service(
    *,
    message: str,
    post_id: UUID,
    db: AsyncSession,
    user: User,
) -> Comment:
    new_comment = Comment(message=message, post_id=post_id, author=user)
    db.add(new_comment)
    await db.flush()
    return new_comment


async def get_comment_service(comment_id: UUID, db: AsyncSession) -> Comment | None:
    comment = await get_comment_by_id_db(
        comment_id,
        db,
        selectinload(Comment.author),
        selectinload(Comment.post).selectinload(Post.author),
    )
    if comment is None:
        raise FieldNotFoundException("comment", str(comment_id))

    return comment


async def update_comment_service(
    form_data: CommentUpdate, comment: Comment, db: AsyncSession
) -> Comment:
    for key, val in form_data.model_dump().items():
        setattr(comment, key, val)

    await db.flush()

    return comment


async def my_comments_service(
    db: AsyncSession, current_user: User, page: int, limit: int
):
    offset = (page - 1) * limit

    return await get_user_comments_db(
        current_user.id,
        db,
        offset,
        limit,
        selectinload(Comment.post).selectinload(Post.author),
        selectinload(Comment.author),
    )
