from typing import Type
from sqlalchemy.orm import Session
from src.database import models
from src import schemas


async def get_users(db: Session) -> list[Type[models.User]]:
    users = db.query(models.User).all()
    return users


async def get_user_by_email(email: str, db: Session) -> models.User | None:
    return db.query(models.User).filter_by(email=email).first()


async def get_user_by_id(user_id: int, db: Session) -> models.User | None:
    return db.query(models.User).filter_by(id=user_id).first()


async def get_user_by_name(user_name: str, db: Session) -> models.User | None:
    return db.query(models.User).filter_by(name=user_name).first()


async def create_user(body: schemas.UserCreate, db: Session) -> models.User:
    new_user = models.User(
        name=body.name, email=body.email, password=body.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: models.User, refresh_token, db: Session) -> None:
    user.refresh_token = refresh_token
    db.commit()