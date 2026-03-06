from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def _get_user_db(filter_condition, db: AsyncSession) -> User | None:
    stmt = select(User).where(filter_condition, User.is_deleted.is_(False))

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user


async def get_active_user_by_id_db(user_id: UUID, db: AsyncSession) -> User | None:
    return await _get_user_db(User.id == user_id, db)


async def get_active_user_by_username_db(
    username: str, db: AsyncSession
) -> User | None:
    return await _get_user_db(User.username == username, db)


async def add_user_db(user: User, db: AsyncSession):
    db.add(user)
    await db.flush()


async def get_all_active_users_db(db: AsyncSession):
    result = await db.execute(select(User).where(User.is_deleted.is_(False)))
    users = result.scalars().all()

    return users
