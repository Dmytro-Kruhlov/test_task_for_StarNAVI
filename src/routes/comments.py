from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from src.repository import comments as repository_comments
from src.repository import posts as repository_posts
from src.database import models
from src import schemas
from src.database.db import get_db
from src.services.auth import auth_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
async def create_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    db_post = await repository_posts.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return await repository_comments.create_comment(db=db, comment=comment, post_id=post_id, user_id=current_user.id)


@router.get("/posts/{post_id}/comments/", response_model=List[schemas.Comment])
async def read_comments(post_id: int, db: Session = Depends(get_db)):
    comments = await repository_comments.get_comments_by_post(db, post_id=post_id)
    return comments


@router.get("/comments-daily-breakdown/")
async def get_comments_breakdown(date_from: datetime, date_to: datetime, db: Session = Depends(get_db)):
    return await repository_comments.get_comments_breakdown(db, date_from=date_from, date_to=date_to)

