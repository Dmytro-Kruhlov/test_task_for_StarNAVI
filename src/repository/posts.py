from sqlalchemy.orm import Session, joinedload

from src import schemas
from src.database import models


async def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), user_id=user_id)
    # Добавить логику проверки поста
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


async def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Post)
        .options(
            joinedload(models.Post.comments).joinedload(models.Comment.author),
            joinedload(models.Post.owner)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


async def get_post(db: Session, post_id: int):
    return (
        db.query(models.Post)
        .options(
            joinedload(models.Post.comments).joinedload(models.Comment.author),
            joinedload(models.Post.owner)
        )
        .filter(models.Post.id == post_id)
        .first()
    )

