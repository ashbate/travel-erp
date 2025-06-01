from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models
from app.services.booking_service import BookingService
from app.database import get_db

router = APIRouter()

def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    return BookingService(db_session=db)

@router.post("/", response_model=schemas.BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_create: schemas.BookingCreate,
    service: BookingService = Depends(get_booking_service)
):
    try:
        return service.create_booking(booking_create=booking_create)
    except ValueError as e: # Handles cases like tour capacity exceeded, guest/tour not found
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/{booking_id}", response_model=schemas.BookingRead)
def read_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service)
):
    db_booking = service.get_booking_by_id(booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return db_booking

@router.get("/guest/{guest_id}", response_model=List[schemas.BookingRead])
def read_bookings_for_guest(
    guest_id: int,
    skip: int = 0,
    limit: int = 100,
    service: BookingService = Depends(get_booking_service)
):
    # Add check if guest exists? Depends on requirements.
    return service.get_bookings_for_guest(guest_id=guest_id, skip=skip, limit=limit)

@router.get("/tour/{tour_id}", response_model=List[schemas.BookingRead])
def read_bookings_for_tour(
    tour_id: int,
    skip: int = 0,
    limit: int = 100,
    service: BookingService = Depends(get_booking_service)
):
    # Add check if tour exists?
    return service.get_bookings_for_tour(tour_id=tour_id, skip=skip, limit=limit)

@router.put("/{booking_id}/status", response_model=schemas.BookingRead)
def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingUpdate, # Re-using BookingUpdate, or a dedicated schema for status
    service: BookingService = Depends(get_booking_service)
):
    if status_update.status is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status field is required.")
    try:
        # The service method update_booking_status expects just the status string.
        updated_booking = service.update_booking_status(booking_id=booking_id, status=status_update.status)
        if updated_booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        return updated_booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.post("/{booking_id}/cancel", response_model=schemas.BookingRead)
def cancel_booking_endpoint( # Renamed to avoid conflict
    booking_id: int,
    service: BookingService = Depends(get_booking_service)
):
    try:
        cancelled_booking = service.cancel_booking(booking_id=booking_id)
        if cancelled_booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        return cancelled_booking
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# --- Booking Room Assignments ---
@router.post("/{booking_id}/room_assignments/", response_model=schemas.BookingRoomAssignmentRead, status_code=status.HTTP_201_CREATED)
def assign_room_to_booking(
    booking_id: int,
    assignment_create: schemas.BookingRoomAssignmentCreate,
    service: BookingService = Depends(get_booking_service)
):
    try:
        assignment = service.assign_room_to_booking(booking_id=booking_id, assignment_create=assignment_create)
        if assignment is None: # Should not happen if exceptions are raised correctly from service
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to assign room. Invalid input or resource not found.")
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/{booking_id}/room_assignments/", response_model=List[schemas.BookingRoomAssignmentRead])
def get_booking_room_assignments(
    booking_id: int,
    service: BookingService = Depends(get_booking_service)
):
    db_booking = service.get_booking_by_id(booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return service.get_room_assignments_for_booking(booking_id=booking_id)

@router.put("/room_assignments/{assignment_id}", response_model=schemas.BookingRoomAssignmentRead)
def update_booking_room_assignment(
    assignment_id: int,
    assignment_update: schemas.BookingRoomAssignmentUpdate,
    service: BookingService = Depends(get_booking_service)
):
    try:
        updated_assignment = service.update_room_assignment(assignment_id=assignment_id, assignment_update=assignment_update)
        if updated_assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room assignment not found")
        return updated_assignment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/room_assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_booking_room_assignment(
    assignment_id: int,
    service: BookingService = Depends(get_booking_service)
):
    removed_assignment = service.remove_room_assignment(assignment_id=assignment_id)
    if removed_assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room assignment not found")
    return
