from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone

from sqlalchemy.orm import selectinload

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.core.utils import parse_user_data
from app.exceptions.exception import (
    InvalidCredentialsError,
    raise_duplicate_from_integrity_error,
)
from app.models.user import User, UserDeletion
from app.repositories.comment import limit_comment_db
from app.repositories.post import limit_post_db
from app.repositories.user import (
    add_user_db,
    get_active_user_by_id_db,
    get_active_user_by_username_db,
    get_all_active_users_db,
)
from app.schemas.user import DeleteProfile, UserCreate, UserUpdate


UPDATE_USER_ALLOWED = {"first_name", "last_name", "username", "email"}


async def sign_in_service(
    form_data: OAuth2PasswordRequestForm,
    db: AsyncSession,
):
    user = await get_active_user_by_username_db(form_data.username, db)

    if not user or not verify_password(form_data.password, user.password):
        raise InvalidCredentialsError()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token,
    }


async def sign_up_service(form_data: UserCreate, db: AsyncSession):
    new_user = User(
        first_name=form_data.first_name.strip().title(),
        last_name=form_data.last_name.strip().title(),
        username=form_data.username,
        email=form_data.email.strip(),
        password=hash_password(form_data.password),
        is_deleted=False,
    )

    try:
        await add_user_db(new_user, db)

    except IntegrityError as e:
        raise_duplicate_from_integrity_error(
            e, {"username": new_user.username, "email": new_user.email}
        )
        raise  # reraise not known unique constraint error or other integrity error

    return {
        "message": "You've successfully created your account. You can now log in with it"
    }


async def my_profile_service(user_id: UUID, db: AsyncSession, page: int, limit: int):
    offlimit = (page - 1) * limit

    return await get_active_user_by_id_db(user_id, db, selectinload(User.posts))


async def get_activate_user_with_activities_service(
    db: AsyncSession, current_user: User, page: int, limit: int
):
    offset = (page - 1) * limit

    posts = await limit_post_db(current_user.id, db, offset, limit)
    comments = await limit_comment_db(current_user.id, db, offset, limit)

    return {
        "posts": posts,
        "comments": comments,
    }


async def update_profile_service(
    form_data: UserUpdate,
    db: AsyncSession,
    current_user: User,
):
    user_data = form_data.model_dump(exclude_unset=True)
    parsed_user = parse_user_data(user_data)

    parsed_user = {k: v for k, v in parsed_user.items() if k in UPDATE_USER_ALLOWED}

    try:

        for key, value in parsed_user.items():
            setattr(current_user, key, value)

        await db.flush()

    except IntegrityError as e:
        raise_duplicate_from_integrity_error(
            e,
            {
                "username": parsed_user.get("username"),
                "email": parsed_user.get("email"),
            },
        )
        raise  # reraise not known unique constraint error

    await db.refresh(current_user)

    return current_user


async def get_user_service(
    user_id: UUID,
    db: AsyncSession,
    current_user: User,
):
    return await get_active_user_by_id_db(user_id, db)


async def get_users_service(db: AsyncSession, page: int, limit: int):
    offset = (page - 1) * limit

    return await get_all_active_users_db(db, offset, limit)


async def delete_profile_service(
    form_data: DeleteProfile,
    db: AsyncSession,
    current_user: User,
):
    if not verify_password(form_data.password, current_user.password):
        raise InvalidCredentialsError()

    current_user.is_deleted = True  # soft delete user

    db.add(
        UserDeletion(
            user_id=current_user.id,
            deleted_at=datetime.now(timezone.utc),
            reason=form_data.reason,
        )
    )

    await db.flush()
