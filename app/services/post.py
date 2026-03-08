import math
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions.exception import FieldNotFoundException
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.repositories.post import (
    add_post_db,
    feed_post_db,
    feed_post_db_web,
    get_all_user_post_db,
    get_post_by_id_db,
)
from app.repositories.user import get_active_user_by_id_db
from app.schemas.post import PostCreate, PostUpdate


UPDATE_POST_ALLOWED = {"title", "content"}


async def my_profile_service(user_id: UUID, db: AsyncSession) -> User | None:
    return await get_active_user_by_id_db(
        user_id,
        db,
        selectinload(User.posts)
        .selectinload(Post.comments)
        .selectinload(Comment.author),
    )


async def feed_post_service(db: AsyncSession, page: int, limit: int) -> List[Post]:
    offset = (page - 1) * limit

    return await feed_post_db(
        db, offset, limit, selectinload(Post.author), selectinload(Post.comments)
    )


async def feed_post_service_web(
    db: AsyncSession,
    page: int,
    limit: int,
) -> tuple[list[Post], int]:
    offset = (page - 1) * limit

    posts, total = await feed_post_db_web(
        db,
        offset,
        limit,
        selectinload(Post.author),
        selectinload(Post.comments).selectinload(Comment.author),
    )

    pages = math.ceil(total / limit) if total else 1
    return posts, pages


async def my_posts_service(db: AsyncSession, current_user: User, page: int, limit: int):
    offset = (page - 1) * limit

    return await get_all_user_post_db(
        db,
        current_user,
        offset,
        limit,
        selectinload(Post.comments).selectinload(Comment.author),
    )


async def create_post_service(
    form_data: PostCreate,
    db: AsyncSession,
    current_user: User,
):
    post = Post(
        title=form_data.title, content=form_data.content, user_id=current_user.id
    )
    return await add_post_db(post, db)


async def get_post_service(post_id: UUID, db: AsyncSession):
    post = await get_post_by_id_db(post_id, db)
    if not post:
        raise FieldNotFoundException("post", str(post_id))

    return post


async def update_post_service(form_data: PostUpdate, post: Post, db: AsyncSession):
    data = form_data.model_dump(exclude_unset=True)
    to_update = {k: v for k, v in data.items() if k in UPDATE_POST_ALLOWED}

    if not to_update:
        return post

    for key, val in to_update.items():
        setattr(post, key, val)

    await db.flush()
    await db.refresh(post)

    return post
