from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.conf import messages
from src.database import models
from src.database.db import get_db
from src.services.auth import auth_service
from src import schemas
from src.repository import users as repository_users


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(auth_service.get_current_user),
) -> models.User:
    return current_user


@router.patch("/settings", response_model=schemas.User)
async def change_user_settings(
    auto_reply: bool,
    auto_reply_delay: int = 60,
    current_user: models.User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
) -> models.User:
    return await repository_users.update_settings(current_user, auto_reply, auto_reply_delay, db)

