from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app import schemas, models # models needed if you type hint current_user for other things
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.database import get_db
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db_session=db)

@router.post("/", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
) -> Any:
    """
    Logs in a user and returns an access token.

    The client should send username and password in a www-form-urlencoded body.
    FastAPI's OAuth2PasswordRequestForm handles this.
    """
    user = service.authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
