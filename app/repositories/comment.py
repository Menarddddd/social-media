from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.user import User


async def get_user_comments_db(
    user_id: UUID, db: AsyncSession, offset: int, limit: int, *options
):
    stmt = select(Comment).where(Comment.user_id == user_id).offset(offset).limit(limit)

    if options:
        stmt = stmt.options(*options)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_comment_by_id_db(
    comment_id: UUID, db: AsyncSession, *options
) -> Comment | None:
    stmt = (
        select(Comment)
        .join(User)
        .where(Comment.id == comment_id, User.is_deleted.is_(False))
    )
    if options:
        stmt = stmt.options(*options)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def limit_comment_db(
    user_id: UUID, db: AsyncSession, offset: int, limit: int, *options
) -> List[Comment]:
    stmt = (
        select(Comment)
        .where(Comment.user_id == user_id)
        .order_by(Comment.date_created.desc())
        .offset(offset)
        .limit(limit)
    )

    if options:
        stmt = stmt.options(*options)

    result = await db.execute(stmt)
    comment = result.scalars().all()

    return list(comment)


async def delete_comment_db(comment: Comment, db: AsyncSession):
    await db.delete(comment)
    await db.flush()
