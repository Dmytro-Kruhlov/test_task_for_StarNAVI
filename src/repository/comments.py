from datetime import datetime

from sqlalchemy import func, Integer
from sqlalchemy.orm import Session
from src import schemas
from src.database import models


async def create_comment(db: Session, comment: schemas.CommentCreate, post_id: int, user_id: int) -> models.Comment:
    db_comment = models.Comment(**comment.model_dump(), post_id=post_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def get_comments_by_post(db: Session, post_id: int) -> list[[models.Comment]]:
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()


async def get_comment(db: Session, comment_id: int) -> models.Comment | None:
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


async def block_comment(db: Session, comment_id: int) -> models.Comment | None:
    comment = await get_comment(db, comment_id)
    if comment:
        comment.is_blocked = True
        db.commit()
        db.refresh(comment)
    return comment


async def delete_comment(db: Session, comment_id: int) -> models.Comment | None:
    comment = await get_comment(db, comment_id)
    if comment:
        db.delete(comment)
        db.commit()
    return comment


async def update_comment(db: Session, comment_id: int, comment: schemas.CommentUpdate) -> models.Comment | None:
    updated_comment = await get_comment(db, comment_id)
    if updated_comment:
        updated_comment.content = comment.content
        db.commit()
        db.refresh(updated_comment)
    return updated_comment


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

