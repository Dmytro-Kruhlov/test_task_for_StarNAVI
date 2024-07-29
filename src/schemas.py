from pydantic import BaseModel
from datetime import datetime, timedelta


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    auto_reply_enabled: bool = False
    auto_reply_delay: timedelta = timedelta(hours=1)


class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    auto_reply_enabled: bool
    auto_reply_delay: timedelta

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime
    is_blocked: bool

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"