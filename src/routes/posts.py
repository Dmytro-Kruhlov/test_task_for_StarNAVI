from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.repository import posts as repository_posts
from src.database import models
from src import schemas
from src.database.db import get_db
from src.services.auth import auth_service

router = APIRouter()


@router.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    return repository_posts.create_post(db=db, post=post, user_id=current_user.id)


@router.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = repository_posts.get_posts(db, skip=skip, limit=limit)
    return posts


@router.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = repository_posts.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

