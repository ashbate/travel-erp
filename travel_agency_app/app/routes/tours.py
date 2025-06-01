from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models # Ensure models is imported
from app.services.tour_service import TourService
from app.services.ai_service import AIService
from app.database import get_db
from app.core.security import get_current_active_user # Import authentication dependency

router = APIRouter()

def get_tour_service(db: Session = Depends(get_db)) -> TourService:
    return TourService(db_session=db)

def get_ai_service() -> AIService:
    return AIService()

@router.post("/", response_model=schemas.TourRead, status_code=status.HTTP_201_CREATED)
def create_tour(
    tour_create: schemas.TourCreate,
    service: TourService = Depends(get_tour_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Ensure the creator is the current authenticated user, or an admin setting it
    # For simplicity now, we assume tour_create.created_by_user_id is correctly set by client
    # or could enforce tour_create.created_by_user_id = current_user.id
    if tour_create.created_by_user_id != current_user.id and current_user.role != 'admin':
        # If non-admin tries to set a different creator
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create tour for another user unless admin.")
    elif tour_create.created_by_user_id is None and current_user.role != 'admin':
        # If creator_id is not provided, default to current user if not admin
        tour_create.created_by_user_id = current_user.id
    elif tour_create.created_by_user_id is None and current_user.role == 'admin':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin must specify created_by_user_id for tour.")

    try:
        return service.create_tour(tour_create=tour_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@router.get("/", response_model=List[schemas.TourRead])
def read_tours(
    skip: int = 0,
    limit: int = 100,
    service: TourService = Depends(get_tour_service)
):
    return service.get_all_tours(skip=skip, limit=limit)

@router.get("/{tour_id}", response_model=schemas.TourRead)
def read_tour(
    tour_id: int,
    service: TourService = Depends(get_tour_service)
):
    # ... (no change, public access for now)
    db_tour = service.get_tour_by_id(tour_id=tour_id)
    if db_tour is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    return db_tour

@router.put("/{tour_id}", response_model=schemas.TourRead)
def update_tour(
    tour_id: int,
    tour_update: schemas.TourUpdate,
    service: TourService = Depends(get_tour_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Add ownership or role check: only creator or admin can update
    db_tour = service.get_tour_by_id(tour_id=tour_id)
    if not db_tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    if db_tour.created_by_user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this tour")
    try:
        updated_tour = service.update_tour(tour_id=tour_id, tour_update=tour_update)
        # ... (rest of the logic)
        if updated_tour is None: # Should be caught by db_tour check above
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found during update")
        return updated_tour
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/{tour_id}", response_model=schemas.TourRead) # Or perhaps just status code 204
def delete_tour(
    tour_id: int,
    service: TourService = Depends(get_tour_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Add ownership or role check: only creator or admin can delete
    db_tour = service.get_tour_by_id(tour_id=tour_id)
    if not db_tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    if db_tour.created_by_user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this tour")
    try:
        deleted_tour = service.delete_tour(tour_id=tour_id)
        # ... (rest of the logic)
        if deleted_tour is None: # Should be caught by db_tour check above
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found during delete attempt")
        return deleted_tour # Or return status.HTTP_204_NO_CONTENT
    except ValueError as e: # If service raises ValueError for business rule violation (e.g., active bookings)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# --- Tour Hotel Allocations (all protected) ---
@router.post("/{tour_id}/hotel_allocations/", response_model=schemas.TourHotelAllocationRead, status_code=status.HTTP_201_CREATED)
def add_hotel_allocation_to_tour(
    tour_id: int,
    allocation_create: schemas.TourHotelAllocationCreate,
    service: TourService = Depends(get_tour_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Add role/ownership check for tour_id
    db_tour = service.get_tour_by_id(tour_id=tour_id)
    if not db_tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    if db_tour.created_by_user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this tour's allocations")
    try:
        allocation = service.add_hotel_allocation_to_tour(tour_id=tour_id, allocation_create=allocation_create)
        # ... (rest of the logic)
        if allocation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to add allocation. Invalid data or resources.")
        return allocation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# Other TourHotelAllocation endpoints (GET, PUT, DELETE) should also be similarly protected.
# For brevity, I'll assume similar protection logic (check tour ownership/admin) for them.

@router.post("/generate-with-ai", response_model=schemas.AIGeneratedItinerary, tags=["Tours", "AI Generation"])
async def generate_tour_itinerary_with_ai(
    prompt: schemas.AITourPrompt,
    ai_service: AIService = Depends(get_ai_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    try:
        generated_itinerary = ai_service.generate_itinerary(prompt_data=prompt)
        return generated_itinerary
    except Exception as e:
        # Log the exception e (e.g., using a proper logger)
        print(f"Error during AI itinerary generation: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service error: {str(e)}")

# GET /hotel_allocations/ and PUT/DELETE for individual allocations also need protection.
# Example for one:
@router.put("/hotel_allocations/{allocation_id}", response_model=schemas.TourHotelAllocationRead)
def update_tour_hotel_allocation(
    allocation_id: int,
    allocation_update: schemas.TourHotelAllocationUpdate,
    service: TourService = Depends(get_tour_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Check ownership of the tour linked to this allocation or admin role
    allocation = service.db.query(models.TourHotelAllocation).filter(models.TourHotelAllocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel allocation not found")
    db_tour = service.get_tour_by_id(tour_id=allocation.tour_id)
    if not db_tour or (db_tour.created_by_user_id != current_user.id and current_user.role != 'admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this allocation")
    # ... (rest of the logic from original subtask) ...
    try:
        updated_allocation = service.update_hotel_allocation(allocation_id=allocation_id, allocation_update=allocation_update)
        if updated_allocation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel allocation not found during update")
        return updated_allocation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/{tour_id}/hotel_allocations/", response_model=List[schemas.TourHotelAllocationRead])
def get_tour_hotel_allocations(
    tour_id: int,
    service: TourService = Depends(get_tour_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    db_tour = service.get_tour_by_id(tour_id=tour_id)
    if db_tour is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    # Optionally, restrict access based on ownership or role, though often allocations are viewable if tour is.
    # For now, if user can get the tour, they can get its allocations by tour_id.
    # If more granular control is needed, add:
    # if db_tour.created_by_user_id != current_user.id and current_user.role != 'admin':
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these allocations")
    return service.get_hotel_allocations_for_tour(tour_id=tour_id)

@router.delete("/hotel_allocations/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tour_hotel_allocation(
    allocation_id: int,
    service: TourService = Depends(get_tour_service),
    current_user: models.User = Depends(get_current_active_user) # Protected
):
    # Check ownership of the tour linked to this allocation or admin role
    allocation = service.db.query(models.TourHotelAllocation).filter(models.TourHotelAllocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel allocation not found")
    db_tour = service.get_tour_by_id(tour_id=allocation.tour_id)
    if not db_tour or (db_tour.created_by_user_id != current_user.id and current_user.role != 'admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this allocation")

    try:
        removed_allocation = service.remove_hotel_allocation(allocation_id=allocation_id)
        if removed_allocation is None: # Should be caught by the check above
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel allocation not found during delete")
        return # Returns 204 No Content
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
