from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models # Ensure models is imported
from app.services.user_service import UserService
from app.database import get_db
from app.core.security import get_current_active_user, RoleChecker # Import RoleChecker

router = APIRouter()

admin_only = RoleChecker(allowed_roles=["admin"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db_session=db)

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_create: schemas.UserCreate,
    service: UserService = Depends(get_user_service),
    # current_admin: models.User = Depends(admin_only) # Only admin can create users for now
    # OR allow self-registration if desired, then remove admin_only for this.
    # For this iteration, let's assume only admins create other users.
    requesting_user: models.User = Depends(get_current_active_user) # Check who is making request
):
    if requesting_user.role != 'admin' and user_create.role == 'admin':
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create other admin users.")
    if requesting_user.role != 'admin' and user_create.username != requesting_user.username:
        # Non-admins cannot create users other than potentially themselves if self-registration was enabled.
        # For now, if user_create is for someone else and not admin, it's forbidden.
        # This logic can be adjusted if self-registration is a feature.
        # For now, we assume only admins use this POST to create any user.
        if requesting_user.role != 'admin': # Simplified: only admin can use POST /users/
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create users.")
    try:
        return service.create_user(user_create=user_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/me", response_model=schemas.UserRead)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Get current logged in user.
    """
    return current_user

@router.get("/", response_model=List[schemas.UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
    current_admin: models.User = Depends(admin_only) # Admin only
):
    return service.get_all_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(get_current_active_user) # Authenticated access
):
    if current_user.role != 'admin' and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
    db_user = service.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(get_current_active_user) # Authenticated access
):
    if current_user.role != 'admin' and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    if user_update.role and user_update.role == 'admin' and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can assign admin role.")
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
    service: UserService = Depends(get_user_service),
    current_admin: models.User = Depends(admin_only) # Admin only
):
    # Prevent admin from deleting themselves? (Optional rule)
    # if current_admin.id == user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin users cannot delete themselves.")
    try:
        deleted_user = service.delete_user(user_id=user_id)
        if deleted_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
