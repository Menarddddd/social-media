from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str = Field(min_length=1, max_length=500)


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: UUID


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str


class PostPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    content: str
    author: UserPublic


class CommentWithAuthorResponse(CommentBase):
    id: UUID
    author: UserPublic


class CommentWithPostAuthorResponse(CommentBase):
    id: UUID
    post: PostPublic


class CommentLoadedResponse(CommentBase):
    id: UUID
    author: UserPublic
    post: PostPublic


class CommentUpdate(BaseModel):
    message: str = Field(min_length=1, max_length=500)
