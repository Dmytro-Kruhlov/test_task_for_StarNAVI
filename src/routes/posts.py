from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.repository import posts as repository_posts
from src.database import models
from src import schemas
from src.database.db import get_db
from src.services.auth import auth_service
from src.services import google_perspective_api as gpa

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/posts/", response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    cur_post = await repository_posts.create_post(db=db, post=post, user_id=current_user.id)
    if not cur_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user in database")
    is_toxic = await gpa.analyze_comment_content(cur_post.content)
    if is_toxic:
        return await repository_posts.block_post(db, cur_post.id)
    return cur_post


@router.get("/posts/", response_model=List[schemas.Post])
async def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = await repository_posts.get_posts(db, skip=skip, limit=limit)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found")
    return posts


@router.get("/posts/{post_id}", response_model=schemas.Post)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    post = await repository_posts.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

