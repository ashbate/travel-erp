from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app import schemas

class TourService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_tour_by_id(self, tour_id: int) -> Optional[models.Tour]:
        return self.db.query(models.Tour).filter(models.Tour.id == tour_id).first()

    def get_all_tours(self, skip: int = 0, limit: int = 100) -> List[models.Tour]:
        return self.db.query(models.Tour).offset(skip).limit(limit).all()

    def create_tour(self, tour_create: schemas.TourCreate) -> models.Tour:
        db_tour = models.Tour(**tour_create.model_dump())
        # In a real app, you might want to fetch the creator user to ensure validity
        # db_user = self.db.query(models.User).filter(models.User.id == tour_create.created_by_user_id).first()
        # if not db_user:
        #     raise ValueError("Creator user not found")
        self.db.add(db_tour)
        self.db.commit()
        self.db.refresh(db_tour)
        return db_tour

    def update_tour(self, tour_id: int, tour_update: schemas.TourUpdate) -> Optional[models.Tour]:
        db_tour = self.get_tour_by_id(tour_id)
        if not db_tour:
            return None

        update_data = tour_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tour, key, value)

        self.db.add(db_tour)
        self.db.commit()
        self.db.refresh(db_tour)
        return db_tour

    def delete_tour(self, tour_id: int) -> Optional[models.Tour]:
        db_tour = self.get_tour_by_id(tour_id)
        if not db_tour:
            return None
        # Add logic here: check for active bookings before deleting? Or handle cascade deletes in DB.
        # For now, direct delete:
        self.db.delete(db_tour)
        self.db.commit()
        return db_tour

    def add_hotel_allocation_to_tour(self, tour_id: int, allocation_create: schemas.TourHotelAllocationCreate) -> Optional[models.TourHotelAllocation]:
        db_tour = self.get_tour_by_id(tour_id)
        if not db_tour:
            # Or raise HTTPException(status_code=404, detail="Tour not found") in API layer
            return None

        # Validate hotel_id and room_configuration_id exist
        db_hotel = self.db.query(models.Hotel).filter(models.Hotel.id == allocation_create.hotel_id).first()
        if not db_hotel:
            # raise ValueError("Hotel not found")
            return None

        db_room_config = self.db.query(models.RoomConfiguration).filter(
            models.RoomConfiguration.id == allocation_create.room_configuration_id,
            models.RoomConfiguration.hotel_id == allocation_create.hotel_id
        ).first()
        if not db_room_config:
            # raise ValueError("RoomConfiguration not found for the given hotel")
            return None

        # Check if allocation exceeds available rooms in room_config (simplified check)
        # A more robust check would consider existing allocations for this room_config across all tours for overlapping dates.
        if db_room_config.number_of_available_rooms < allocation_create.allocated_rooms:
            # raise ValueError("Not enough available rooms for this configuration")
            return None

        db_allocation = models.TourHotelAllocation(**allocation_create.model_dump(), tour_id=tour_id)
        self.db.add(db_allocation)
        self.db.commit()
        self.db.refresh(db_allocation)
        return db_allocation

    def get_hotel_allocations_for_tour(self, tour_id: int) -> List[models.TourHotelAllocation]:
        return self.db.query(models.TourHotelAllocation).filter(models.TourHotelAllocation.tour_id == tour_id).all()

    def update_hotel_allocation(self, allocation_id: int, allocation_update: schemas.TourHotelAllocationUpdate) -> Optional[models.TourHotelAllocation]:
        db_allocation = self.db.query(models.TourHotelAllocation).filter(models.TourHotelAllocation.id == allocation_id).first()
        if not db_allocation:
            return None

        update_data = allocation_update.model_dump(exclude_unset=True)
        # Add validation if needed (e.g., allocated_rooms vs room_config.number_of_available_rooms)
        for key, value in update_data.items():
            setattr(db_allocation, key, value)

        self.db.add(db_allocation)
        self.db.commit()
        self.db.refresh(db_allocation)
        return db_allocation

    def remove_hotel_allocation(self, allocation_id: int) -> Optional[models.TourHotelAllocation]:
        db_allocation = self.db.query(models.TourHotelAllocation).filter(models.TourHotelAllocation.id == allocation_id).first()
        if not db_allocation:
            return None

        # Consider implications: are there bookings assigned to rooms in this allocation?
        self.db.delete(db_allocation)
        self.db.commit()
        return db_allocation
