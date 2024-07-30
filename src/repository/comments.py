from datetime import datetime

from sqlalchemy import func, Integer
from sqlalchemy.orm import Session
from src import schemas
from src.database import models


async def create_comment(db: Session, comment: schemas.CommentCreate, post_id: int, user_id: int):
    db_comment = models.Comment(**comment.dict(), post_id=post_id, user_id=user_id)
    # # Добавить логику бана коментариев
    # if is_comment_blocked(comment.content):
    #     db_comment.is_blocked = True
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def is_comment_blocked(content: str) -> bool:
    # Simple example check for profanity
    blocked_words = ["badword1", "badword2"]
    for word in blocked_words:
        if word in content.lower():
            return True
    return False


async def get_comments_by_post(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()


async def get_comments_breakdown(db: Session, date_from: datetime, date_to: datetime):

    stats = db.query(
        models.Comment.post_id,
        func.date(models.Comment.created_at).label('date'),
        func.count(models.Comment.id).label('total_comments'),
        func.sum(models.Comment.is_blocked.cast(Integer)).label('blocked_comments')
    ).filter(
        models.Comment.created_at >= date_from,
        models.Comment.created_at <= date_to
    ).group_by(
        models.Comment.post_id,
        func.date(models.Comment.created_at)
    ).all()

    results = {}
    for stat in stats:
        if stat.post_id not in results:
            results[stat.post_id] = []
        results[stat.post_id].append({
            "date": stat.date,
            "total_comments": stat.total_comments,
            "blocked_comments": stat.blocked_comments
        })

    final_results = [{"post_id": post_id, "stats": stats} for post_id, stats in results.items()]

    return final_results

