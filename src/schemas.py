from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    auto_reply_enabled: bool
    auto_reply_delay: int

    class ConfigDict:
        from_attributes = True


class PostBase(BaseModel):
    title: str = Field(min_length=2)
    content: str = Field(min_length=5)


class PostCreate(PostBase):
    pass


class Comment(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    is_blocked: bool
    created_at: datetime
    parent_comment: Optional[int]
    author: User

    class ConfigDict:
        from_attributes = True


class Post(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    is_blocked: bool
    owner: User
    comments: List[Comment] = []

    class ConfigDict:
        from_attributes = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"



