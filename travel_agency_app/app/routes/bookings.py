from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models # Ensure models is imported
from app.services.booking_service import BookingService
from app.database import get_db
from app.core.security import get_current_active_user, RoleChecker # Import security dependencies

router = APIRouter()
admin_agent_roles = RoleChecker(allowed_roles=["admin", "agent"]) # Define RoleChecker instance
admin_only = RoleChecker(allowed_roles=["admin"])

def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    return BookingService(db_session=db)

@router.post("/", response_model=schemas.BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_create: schemas.BookingCreate,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Potentially link booking to current_user if that's a business rule (e.g. agent creating it)
    # For now, guest_id in booking_create is primary link. Access control is via auth.
    try:
        return service.create_booking(booking_create=booking_create)
    except ValueError as e: # Handles cases like tour capacity exceeded, guest/tour not found
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/{booking_id}", response_model=schemas.BookingRead)
def read_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    db_booking = service.get_booking_by_id(booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    # Add ownership or role check: User can see their own bookings (if guest linked to user) or admin sees all.
    # This requires linking Guest to User or Booking to User (agent). For now, any authenticated user can see any booking by ID.
    # This should be refined based on how guests/users are related to bookings.
    # Example:
    # if current_user.role not in ['admin', 'agent'] and db_booking.guest.user_id != current_user.id: # Assuming guest has a user_id link
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this booking")
    return db_booking

@router.get("/guest/{guest_id}", response_model=List[schemas.BookingRead])
def read_bookings_for_guest(
    guest_id: int,
    skip: int = 0,
    limit: int = 100,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Similar to above: refine access based on user-guest relationship or admin role.
    # Example:
    # guest_service = GuestService(db) # Assuming GuestService exists
    # target_guest = guest_service.get_guest_by_id(guest_id)
    # if not target_guest or (current_user.role not in ['admin', 'agent'] and target_guest.user_id != current_user.id):
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these bookings")
    return service.get_bookings_for_guest(guest_id=guest_id, skip=skip, limit=limit)

@router.get("/tour/{tour_id}", response_model=List[schemas.BookingRead])
def read_bookings_for_tour(
    tour_id: int,
    skip: int = 0,
    limit: int = 100,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Generally, bookings for a tour are more public if the tour itself is public, or visible to agents/admins.
    # TourService could be used to check if tour_id exists.
    return service.get_bookings_for_tour(tour_id=tour_id, skip=skip, limit=limit)

@router.put("/{booking_id}/status", response_model=schemas.BookingRead)
def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingUpdate,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    db_booking = service.get_booking_by_id(booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if current_user.role not in ['admin', 'agent']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update booking status")

    if status_update.status is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status field is required.")
    try:
        updated_booking = service.update_booking_status(booking_id=booking_id, status=status_update.status)
        if updated_booking is None: # Should be caught by the check above
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found during status update")
        return updated_booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.post("/{booking_id}/cancel", response_model=schemas.BookingRead)
def cancel_booking_endpoint(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    db_booking = service.get_booking_by_id(booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # Example: Allow admin, agent, or user who 'owns' booking (if applicable)
    if current_user.role not in ['admin', 'agent']: # Add more specific ownership check if needed
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel booking")

    try:
        cancelled_booking = service.cancel_booking(booking_id=booking_id)
        if cancelled_booking is None: # Should be caught by the check above
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found during cancellation")
        return cancelled_booking
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# --- BookingRoomAssignment Services ---
@router.post("/{booking_id}/room_assignments/", response_model=schemas.BookingRoomAssignmentRead, status_code=status.HTTP_201_CREATED)
def assign_room_to_booking(
    booking_id: int,
    assignment_create: schemas.BookingRoomAssignmentCreate,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    # Ensure booking exists and potentially check if current_user is allowed to modify this booking
    db_booking = service.get_booking_by_id(booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    # Add more specific ownership check for the booking if necessary for non-admins/agents

    try:
        assignment = service.assign_room_to_booking(booking_id=booking_id, assignment_create=assignment_create)
        if assignment is None:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to assign room. Invalid input or resource not found.")
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/{booking_id}/room_assignments/", response_model=List[schemas.BookingRoomAssignmentRead])
def get_booking_room_assignments(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    db_booking = service.get_booking_by_id(booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    # Add specific ownership/role check if necessary, similar to read_booking
    return service.get_room_assignments_for_booking(booking_id=booking_id)

@router.put("/room_assignments/{assignment_id}", response_model=schemas.BookingRoomAssignmentRead)
def update_booking_room_assignment(
    assignment_id: int,
    assignment_update: schemas.BookingRoomAssignmentUpdate,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    # Check if assignment exists and if user is allowed to modify it (e.g., based on booking ownership)
    db_assignment = service.db.query(models.BookingRoomAssignment).filter(models.BookingRoomAssignment.id == assignment_id).first()
    if not db_assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room assignment not found")
    # Add booking ownership check for non-admins/agents if required

    try:
        updated_assignment = service.update_room_assignment(assignment_id=assignment_id, assignment_update=assignment_update)
        if updated_assignment is None: # Should be caught by above check
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room assignment not found during update")
        return updated_assignment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/room_assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_booking_room_assignment(
    assignment_id: int,
    service: BookingService = Depends(get_booking_service),
    current_user: models.User = Depends(admin_agent_roles) # Agent or Admin
):
    # Similar checks as update
    db_assignment = service.db.query(models.BookingRoomAssignment).filter(models.BookingRoomAssignment.id == assignment_id).first()
    if not db_assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room assignment not found")
    # Add booking ownership check for non-admins/agents if required

    removed_assignment = service.remove_room_assignment(assignment_id=assignment_id)
    if removed_assignment is None: # Should be caught by above check
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room assignment not found during delete")
    return
