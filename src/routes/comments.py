from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from src.repository import comments as repository_comments
from src.repository import posts as repository_posts
from src.repository import users as repository_users
from src.database import models
from src import schemas
from src.database.db import get_db
from src.services.auth import auth_service
from src.services import scheduler
from src.services import google_perspective_api as gpa


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
async def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user),
):
    db_post = await repository_posts.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if db_post.is_blocked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You can't create comment for blocked post")
    db_comment = await repository_comments.create_comment(
        db=db, comment=comment, post_id=post_id, user_id=current_user.id
    )
    is_toxic = await gpa.analyze_comment_content(db_comment.content)
    if is_toxic:
        return await repository_comments.block_comment(db, db_comment.id)
    post_owner = db_post.user_id
    db_post_owner = await repository_users.get_user_by_id(post_owner, db)

    if db_post_owner.auto_reply_enabled:
        delay = db_post_owner.auto_reply_delay
        task, args = scheduler.create_schedule_task(post_owner, db_comment.id, db, delay)
        scheduler.schedule_task(background_tasks, delay * 60, task, *args)
    return db_comment


@router.get("/posts/{post_id}/comments/", response_model=List[schemas.Comment])
async def read_comments(post_id: int, db: Session = Depends(get_db)):
    comments = await repository_comments.get_comments_by_post(db, post_id=post_id)
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found")
    return comments


@router.get("/comments-daily-breakdown/")
async def get_comments_breakdown(date_from: datetime, date_to: datetime, db: Session = Depends(get_db)):
    statistics = await repository_comments.get_comments_breakdown(db, date_from=date_from, date_to=date_to)
    if not statistics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no comments on posts during this period of time")
    return statistics

