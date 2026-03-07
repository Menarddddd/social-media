from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence
from app.models.user import User


async def _get_user_db(filter_condition, db: AsyncSession, *options) -> User | None:
    stmt = select(User).where(filter_condition, User.is_deleted.is_(False))

    if options:
        stmt = stmt.options(*options)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_active_user_by_id_db(
    user_id: UUID, db: AsyncSession, *options
) -> User | None:
    return await _get_user_db(User.id == user_id, db, *options)


async def get_active_user_by_username_db(
    username: str, db: AsyncSession, *options
) -> User | None:
    return await _get_user_db(User.username == username, db, *options)


async def add_user_db(user: User, db: AsyncSession):
    db.add(user)
    await db.flush()


async def get_all_active_users_db(db: AsyncSession, offset: int, limit: int):
    result = await db.execute(
        select(User).where(User.is_deleted.is_(False)).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    return users
