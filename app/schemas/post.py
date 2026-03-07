from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PostBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=1, max_length=100)
    content: str


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: UUID
    date_created: datetime


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str


class CommentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str
    author: UserPublic
    date_created: datetime


class PostWithCommentAuthorResponse(PostBase):
    id: UUID
    comments: list[CommentPublic]


class PostFeedResponse(PostBase):
    id: UUID
    date_created: datetime

    author: UserPublic
    comments: list[CommentPublic]


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
