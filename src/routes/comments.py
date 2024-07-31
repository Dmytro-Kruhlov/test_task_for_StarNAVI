import asyncio

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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
from src.services import llama

# from src.services.scheduler import schedule_task

router = APIRouter(prefix="/comments", tags=["comments"])


# @router.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
# async def create_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_service.get_current_user)):
#     db_post = await repository_posts.get_post(db, post_id=post_id)
#     if db_post is None:
#         raise HTTPException(status_code=404, detail="Post not found")
#     return await repository_comments.create_comment(db=db, comment=comment, post_id=post_id, user_id=current_user.id)


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
        raise HTTPException(status_code=404, detail="Post not found")
    db_comment = await repository_comments.create_comment(
        db=db, comment=comment, post_id=post_id, user_id=current_user.id
    )

    post_owner = db_post.user_id
    db_post_owner = await repository_users.get_user_by_id(post_owner, db)

    if db_post_owner.auto_reply_enabled:
        delay = db_post_owner.auto_reply_delay
        # schedule_task(delay * 60, asyncio.ensure_future, llama.schedule_auto_reply(post_owner, db_comment.id, db, delay))
        task, args = llama.create_schedule_task(post_owner, db_comment.id, db, delay)
        llama.schedule_task(background_tasks, delay * 60, task, *args)
    return db_comment


@router.get("/posts/{post_id}/comments/", response_model=List[schemas.Comment])
async def read_comments(post_id: int, db: Session = Depends(get_db)):
    comments = await repository_comments.get_comments_by_post(db, post_id=post_id)
    return comments


@router.get("/comments-daily-breakdown/")
async def get_comments_breakdown(date_from: datetime, date_to: datetime, db: Session = Depends(get_db)):
    return await repository_comments.get_comments_breakdown(db, date_from=date_from, date_to=date_to)

