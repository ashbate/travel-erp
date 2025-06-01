from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models # Ensure models is imported
from app.services.guest_service import GuestService
from app.database import get_db
from app.core.security import get_current_active_user, RoleChecker # Import

router = APIRouter()
admin_agent_roles = RoleChecker(allowed_roles=["admin", "agent"])
admin_only = RoleChecker(allowed_roles=["admin"])

def get_guest_service(db: Session = Depends(get_db)) -> GuestService:
    return GuestService(db_session=db)

@router.post("/", response_model=schemas.GuestRead, status_code=status.HTTP_201_CREATED)
def create_guest(
    guest_create: schemas.GuestCreate,
    service: GuestService = Depends(get_guest_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    try:
        return service.create_guest(guest_create=guest_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/", response_model=List[schemas.GuestRead])
def read_guests(
    skip: int = 0,
    limit: int = 100,
    service: GuestService = Depends(get_guest_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    return service.get_all_guests(skip=skip, limit=limit)

@router.get("/{guest_id}", response_model=schemas.GuestRead)
def read_guest(
    guest_id: int,
    service: GuestService = Depends(get_guest_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    db_guest = service.get_guest_by_id(guest_id=guest_id)
    if db_guest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
    return db_guest

@router.put("/{guest_id}", response_model=schemas.GuestRead)
def update_guest(
    guest_id: int,
    guest_update: schemas.GuestUpdate,
    service: GuestService = Depends(get_guest_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    try:
        updated_guest = service.update_guest(guest_id=guest_id, guest_update=guest_update)
        if updated_guest is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
        return updated_guest
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guest(
    guest_id: int,
    service: GuestService = Depends(get_guest_service),
    current_user: models.User = Depends(admin_only) # Admin only for deletion
):
    try:
        deleted_guest = service.delete_guest(guest_id=guest_id)
        if deleted_guest is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")
        return # Returns 204 No Content
    except ValueError as e: # If service prevents deletion due to associated bookings
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
