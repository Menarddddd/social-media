import jwt
from typing import Annotated
from uuid import UUID

from jwt import ExpiredSignatureError, PyJWTError
from fastapi import Depends, Cookie, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.settings import settings
from app.models.user import User
from app.repositories.user import get_active_user_by_id_db


async def get_current_user_web(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> User | None:
    if not access_token:
        return None

    try:
        payload = jwt.decode(
            access_token,
            settings.ACCESS_SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
        )

        sub = payload.get("sub")
        if not sub:
            return None

        user_id = UUID(sub)
        user = await get_active_user_by_id_db(user_id, db)
        return user

    except (ExpiredSignatureError, PyJWTError, ValueError):
        return None


async def require_user_web(
    user: Annotated[User | None, Depends(get_current_user_web)],
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/signin"},
        )
    return user
