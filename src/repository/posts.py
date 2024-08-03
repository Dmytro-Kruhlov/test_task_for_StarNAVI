from sqlalchemy.orm import Session, joinedload
from src import schemas
from src.database import models


async def create_post(db: Session, post: schemas.PostCreate, user_id: int) -> models.Post:
    db_post = models.Post(**post.model_dump(), user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


async def get_posts(db: Session, skip: int = 0, limit: int = 10) -> list[[models.Post]]:
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


async def get_post(db: Session, post_id: int) -> models.Post | None:
    return (
        db.query(models.Post)
        .options(
            joinedload(models.Post.comments).joinedload(models.Comment.author),
            joinedload(models.Post.owner)
        )
        .filter(models.Post.id == post_id)
        .first()
    )


async def block_post(db: Session, post_id: int) -> models.Post:
    post = await get_post(db, post_id)
    if post:
        post.is_blocked = True
        db.commit()
        db.refresh(post)
    return post


async def delete_post(db: Session, post_id: int) -> models.Post | None:
    post = await get_post(db, post_id)
    if post:
        db.delete(post)
        db.commit()
    return post


async def update_post(db: Session, post_id: int, post: schemas.PostCreate) -> models.Post | None:
    updated_post = await get_post(db, post_id)
    if updated_post:
        if post.title:
            updated_post.title = post.title
        if post.content:
            updated_post.content = post.content
        db.commit()
        db.refresh(updated_post)
    return updated_post
