from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, Interval
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

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    is_blocked = Column(Boolean, default=False)

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    parent_comment = Column(Integer, ForeignKey("comments.id"), default=None)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


# class CommentReply(Base):
#     __tablename__ = "comment_replies"
#     id = Column(Integer, primary_key=True, index=True)
#     comment_id = Column(Integer, ForeignKey("comments.id"))
#     user_id = Column(Integer, ForeignKey("users.id"))
#     content = Column(Text)
#     created_at = Column(DateTime, server_default=func.now())
#
#     comment = relationship("Comment")
#     author = relationship("User")

