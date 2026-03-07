import jwt
from uuid import UUID
from jwt import ExpiredSignatureError, PyJWTError
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.settings import settings
from app.exceptions.exception import FieldNotFoundException
from app.models.user import User
from app.repositories.comment import get_comment_by_id_db
from app.repositories.post import get_post_by_id_db
from app.repositories.user import get_active_user_by_id_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/signin")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
        )
        sub = payload.get("sub")
        if not sub:
            raise credentials_exc

        try:
            user_id = UUID(sub)

        except ValueError:
            raise credentials_exc

        user = await get_active_user_by_id_db(user_id, db)
        if not user:
            raise credentials_exc

        return user

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except PyJWTError:
        raise credentials_exc


async def post_owner(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    post = await get_post_by_id_db(post_id, db)
    if not post:
        raise FieldNotFoundException("post", str(post_id))

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission to modify this post",
        )

    return post


async def comment_owner(
    comment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    comment = await get_comment_by_id_db(comment_id, db)
    if not comment:
        raise FieldNotFoundException("comment", str(comment_id))

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission to modify this commen",
        )

    return comment
