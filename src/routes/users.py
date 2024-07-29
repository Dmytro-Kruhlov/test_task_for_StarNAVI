
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.models import User
from src.database.db import get_db
from src.services.auth import auth_service
from src import schemas
from src.repository import users as repository_users


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
) -> User:
    return current_user


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = repository_users.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail=messages.EMAIL_ALREADY_EXISTS)
    return repository_users.create_user(body=user, db=db)

