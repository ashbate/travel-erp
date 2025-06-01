from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, models
from app.services.tour_service import TourService
from app.database import get_db
from app.services.ai_service import AIService # Add this

router = APIRouter()

def get_tour_service(db: Session = Depends(get_db)) -> TourService:
    return TourService(db_session=db)

# Add a dependency injector for AIService
def get_ai_service() -> AIService:
    return AIService()

# ... (router definition and other routes)

@router.post("/generate-with-ai", response_model=schemas.AIGeneratedItinerary, tags=["Tours", "AI Generation"])
async def generate_tour_itinerary_with_ai(
    prompt: schemas.AITourPrompt,
    ai_service: AIService = Depends(get_ai_service) # Use the new dependency
    # current_user: models.User = Depends(get_current_active_user) # Optional
):
    """
    Generates a tour itinerary suggestion using an AI model.
    """
    try:
        # Call the actual AI service
        generated_itinerary = ai_service.generate_itinerary(prompt_data=prompt)
        return generated_itinerary
    except Exception as e:
        # Log the exception e (e.g., using a proper logger)
        print(f"Error during AI itinerary generation: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service error: {str(e)}")

@router.post("/", response_model=schemas.TourRead, status_code=status.HTTP_201_CREATED)
def create_tour(
    tour_create: schemas.TourCreate,
    service: TourService = Depends(get_tour_service)
):
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
    db_tour = service.get_tour_by_id(tour_id=tour_id)
    if db_tour is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    return db_tour

@router.put("/{tour_id}", response_model=schemas.TourRead)
def update_tour(
    tour_id: int,
    tour_update: schemas.TourUpdate,
    service: TourService = Depends(get_tour_service)
):
    try:
        updated_tour = service.update_tour(tour_id=tour_id, tour_update=tour_update)
        if updated_tour is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
        return updated_tour
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/{tour_id}", response_model=schemas.TourRead) # Or perhaps just status code 204
def delete_tour(
    tour_id: int,
    service: TourService = Depends(get_tour_service)
):
    try:
        deleted_tour = service.delete_tour(tour_id=tour_id)
        if deleted_tour is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
        return deleted_tour # Or return status.HTTP_204_NO_CONTENT
    except ValueError as e: # If service raises ValueError for business rule violation (e.g., active bookings)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# --- Tour Hotel Allocations ---
@router.post("/{tour_id}/hotel_allocations/", response_model=schemas.TourHotelAllocationRead, status_code=status.HTTP_201_CREATED)
def add_hotel_allocation_to_tour(
    tour_id: int,
    allocation_create: schemas.TourHotelAllocationCreate,
    service: TourService = Depends(get_tour_service)
):
    try:
        allocation = service.add_hotel_allocation_to_tour(tour_id=tour_id, allocation_create=allocation_create)
        if allocation is None:
            # This condition might be hit if tour, hotel, or room_config not found, or other validation fails in service
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour, Hotel, or RoomConfiguration not found, or validation failed.")
        return allocation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/{tour_id}/hotel_allocations/", response_model=List[schemas.TourHotelAllocationRead])
def get_tour_hotel_allocations(
    tour_id: int,
    service: TourService = Depends(get_tour_service)
):
    # Ensure tour exists first
    db_tour = service.get_tour_by_id(tour_id=tour_id)
    if db_tour is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    return service.get_hotel_allocations_for_tour(tour_id=tour_id)

@router.put("/hotel_allocations/{allocation_id}", response_model=schemas.TourHotelAllocationRead)
def update_tour_hotel_allocation(
    allocation_id: int,
    allocation_update: schemas.TourHotelAllocationUpdate,
    service: TourService = Depends(get_tour_service)
):
    try:
        updated_allocation = service.update_hotel_allocation(allocation_id=allocation_id, allocation_update=allocation_update)
        if updated_allocation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel allocation not found")
        return updated_allocation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.delete("/hotel_allocations/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tour_hotel_allocation(
    allocation_id: int,
    service: TourService = Depends(get_tour_service)
):
    try:
        removed_allocation = service.remove_hotel_allocation(allocation_id=allocation_id)
        if removed_allocation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel allocation not found")
        return # Returns 204 No Content
    except ValueError as e: # e.g. if allocation has dependent bookings
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
