from typing import Annotated, List
from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import DeleteProfile, Token, UserCreate, UserResponse, UserUpdate
from app.core.dependency import get_current_user
from app.services.user import (
    delete_profile_service,
    get_user_service,
    get_users_service,
    sign_in_service,
    sign_up_service,
    update_profile_service,
)


router = APIRouter()


@router.post("/signin", response_model=Token, status_code=status.HTTP_200_OK)
async def sign_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await sign_in_service(form_data, db)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(form_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await sign_up_service(form_data, db)


@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_users_service(db, current_user)


@router.get("/profile", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.delete("/delete_user", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete(id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    await db.delete(user)
    await db.commit()


@router.patch("", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    form_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await update_profile_service(form_data, db, current_user)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return get_user_service(user_id, db, current_user)


@router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    form_data: DeleteProfile,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await delete_profile_service(form_data, db, current_user)
