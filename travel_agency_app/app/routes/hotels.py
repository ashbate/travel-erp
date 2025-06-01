from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models # Ensure models is imported
from app.services.hotel_service import HotelService
from app.database import get_db
from app.core.security import get_current_active_user, RoleChecker # Import

router = APIRouter()
admin_agent_roles = RoleChecker(allowed_roles=["admin", "agent"])
admin_only = RoleChecker(allowed_roles=["admin"])

def get_hotel_service(db: Session = Depends(get_db)) -> HotelService:
    return HotelService(db_session=db)

# Hotel Endpoints
@router.post("/", response_model=schemas.HotelRead, status_code=status.HTTP_201_CREATED)
def create_hotel(
    hotel_create: schemas.HotelCreate,
    service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    try:
        return service.create_hotel(hotel_create=hotel_create)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# GET endpoints for hotels and room configs can remain public or be protected as needed.
# For now, making them accessible to any authenticated user (agent/admin).
@router.get("/", response_model=List[schemas.HotelRead])
def read_hotels(
    skip: int = 0, limit: int = 100, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(get_current_active_user) # Any authenticated user
):
    return service.get_all_hotels(skip=skip, limit=limit)

@router.get("/{hotel_id}", response_model=schemas.HotelRead)
def read_hotel(
    hotel_id: int, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(get_current_active_user) # Any authenticated user
):
    db_hotel = service.get_hotel_by_id(hotel_id=hotel_id)
    if db_hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return db_hotel

@router.put("/{hotel_id}", response_model=schemas.HotelRead)
def update_hotel(
    hotel_id: int, hotel_update: schemas.HotelUpdate, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    try:
        updated_hotel = service.update_hotel(hotel_id=hotel_id, hotel_update=hotel_update)
        if updated_hotel is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        return updated_hotel
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hotel(
    hotel_id: int, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(admin_only) # Admin only for deletion
):
    try:
        deleted_hotel = service.delete_hotel(hotel_id=hotel_id)
        if deleted_hotel is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# Room Configuration Endpoints - similar protection
@router.post("/{hotel_id}/room_configurations/", response_model=schemas.RoomConfigurationRead, status_code=status.HTTP_201_CREATED)
def create_room_configuration_for_hotel(
    hotel_id: int, room_config_create_base: schemas.RoomConfigurationBase, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    room_config_create = schemas.RoomConfigurationCreate(**room_config_create_base.model_dump(), hotel_id=hotel_id)
    try:
        return service.create_room_configuration(room_config_create=room_config_create)
    except ValueError as e: # e.g. Hotel not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# GET for room configs - any authenticated user
@router.get("/{hotel_id}/room_configurations/", response_model=List[schemas.RoomConfigurationRead])
def read_room_configurations_for_hotel(
    hotel_id: int, skip: int = 0, limit: int = 100, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(get_current_active_user)
):
    db_hotel = service.get_hotel_by_id(hotel_id=hotel_id)
    if db_hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return service.get_room_configurations_for_hotel(hotel_id=hotel_id, skip=skip, limit=limit)

@router.get("/room_configurations/{room_config_id}", response_model=schemas.RoomConfigurationRead) # Added this missing route from problem description
def read_room_configuration(
    room_config_id: int,
    service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(get_current_active_user) # Any authenticated user
):
    db_room_config = service.get_room_configuration_by_id(room_config_id=room_config_id)
    if db_room_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room configuration not found")
    return db_room_config

@router.put("/room_configurations/{room_config_id}", response_model=schemas.RoomConfigurationRead)
def update_room_configuration(
    room_config_id: int, room_config_update: schemas.RoomConfigurationUpdate, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    try:
        updated_room_config = service.update_room_configuration(room_config_id=room_config_id, room_config_update=room_config_update)
        if updated_room_config is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room configuration not found")
        return updated_room_config
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/room_configurations/{room_config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_configuration(
    room_config_id: int, service: HotelService = Depends(get_hotel_service),
    current_user: models.User = Depends(admin_only) # Admin only for deletion
):
    try:
        deleted_room_config = service.delete_room_configuration(room_config_id=room_config_id)
        if deleted_room_config is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room configuration not found")
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
