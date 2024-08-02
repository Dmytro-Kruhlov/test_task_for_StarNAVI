from src.database import models
from src.repository import users as repository_users
from src.repository import comments as repository_comments
from src.services import llama
import asyncio
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks


async def auto_reply(post_owner_id: int, comment_id: int, db: Session, delay):
    print(f"Executing scheduled task for comment {comment_id}")
    db_comment = await repository_comments.get_comment(db, comment_id)
    db_post_owner = await repository_users.get_user_by_id(post_owner_id, db)
    if db_post_owner.auto_reply_enabled:
        reply_content = await llama.generate_reply(
            db_comment.post.content, db_comment.content, db_post_owner.username
        )
        db_reply = models.Comment(
            post_id=db_comment.post_id,
            user_id=post_owner_id,
            content=reply_content,
            parent_comment=db_comment.id,
        )
        db.add(db_reply)
        db.commit()
        db.refresh(db_reply)
        print(f"Auto reply created for comment {comment_id}")


def create_schedule_task(post_owner_id: int, comment_id: int, db: Session, delay):
    return auto_reply, (post_owner_id, comment_id, db, delay)


def schedule_task(background_tasks: BackgroundTasks, delay: int, task, *args):
    async def wrapper():
        await asyncio.sleep(delay)
        await task(*args)

    background_tasks.add_task(wrapper)
