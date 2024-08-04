from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    auto_reply_enabled = Column(Boolean, default=False)
    auto_reply_delay = Column(Integer, default=60)
    refresh_token = Column(String(255), nullable=True)

    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    is_blocked = Column(Boolean, default=False)

    owner = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    parent_comment = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), default=None
    )

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
