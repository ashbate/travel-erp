from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models
from app.services.user_service import UserService
from app.database import get_db
# Placeholder for auth dependencies: from app.dependencies import get_current_active_user (for later)

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db_session=db)

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_create: schemas.UserCreate,
    service: UserService = Depends(get_user_service)
    # current_user: models.User = Depends(get_current_active_user) # Example for role checks later
):
    # Add role validation here if needed, e.g. only admins can create users or certain roles
    # if current_user.role != 'admin':
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create users")
    try:
        return service.create_user(user_create=user_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/", response_model=List[schemas.UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service)
    # current_user: models.User = Depends(get_current_active_user)
):
    # Add role validation: only admins can see all users?
    return service.get_all_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
    # current_user: models.User = Depends(get_current_active_user)
):
    # Add role validation: can user see only their own profile or admins see all?
    db_user = service.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    service: UserService = Depends(get_user_service)
    # current_user: models.User = Depends(get_current_active_user)
):
    # Add role/ownership validation
    try:
        updated_user = service.update_user(user_id=user_id, user_update=user_update)
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
    # current_user: models.User = Depends(get_current_active_user)
):
    # Add role validation
    try:
        deleted_user = service.delete_user(user_id=user_id)
        if deleted_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return
    except ValueError as e: # e.g. user has created tours
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# Add /users/me endpoint later for authenticated users to get their own info
