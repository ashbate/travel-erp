from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app import schemas

class HotelService:
    def __init__(self, db_session: Session):
        self.db = db_session

    # --- Hotel Methods ---
    def get_hotel_by_id(self, hotel_id: int) -> Optional[models.Hotel]:
        return self.db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()

    def get_all_hotels(self, skip: int = 0, limit: int = 100) -> List[models.Hotel]:
        return self.db.query(models.Hotel).offset(skip).limit(limit).all()

    def create_hotel(self, hotel_create: schemas.HotelCreate) -> models.Hotel:
        db_hotel = models.Hotel(**hotel_create.model_dump())
        self.db.add(db_hotel)
        self.db.commit()
        self.db.refresh(db_hotel)
        return db_hotel

    def update_hotel(self, hotel_id: int, hotel_update: schemas.HotelUpdate) -> Optional[models.Hotel]:
        db_hotel = self.get_hotel_by_id(hotel_id)
        if not db_hotel:
            return None

        update_data = hotel_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_hotel, key, value)

        self.db.add(db_hotel)
        self.db.commit()
        self.db.refresh(db_hotel)
        return db_hotel

    def delete_hotel(self, hotel_id: int) -> Optional[models.Hotel]:
        db_hotel = self.get_hotel_by_id(hotel_id)
        if not db_hotel:
            return None
        # Check for RoomConfigurations or TourHotelAllocations associated with this hotel before deleting.
        if db_hotel.room_configurations or db_hotel.tour_allocations:
            raise ValueError("Hotel cannot be deleted as it has associated room configurations or tour allocations.")
        self.db.delete(db_hotel)
        self.db.commit()
        return db_hotel

    # --- RoomConfiguration Methods ---
    def get_room_configuration_by_id(self, room_config_id: int) -> Optional[models.RoomConfiguration]:
        return self.db.query(models.RoomConfiguration).filter(models.RoomConfiguration.id == room_config_id).first()

    def get_room_configurations_for_hotel(self, hotel_id: int, skip: int = 0, limit: int = 100) -> List[models.RoomConfiguration]:
        return self.db.query(models.RoomConfiguration).filter(models.RoomConfiguration.hotel_id == hotel_id).offset(skip).limit(limit).all()

    def create_room_configuration(self, room_config_create: schemas.RoomConfigurationCreate) -> models.RoomConfiguration:
        db_hotel = self.get_hotel_by_id(room_config_create.hotel_id)
        if not db_hotel:
            raise ValueError("Hotel not found for this room configuration.")

        db_room_config = models.RoomConfiguration(**room_config_create.model_dump())
        self.db.add(db_room_config)
        self.db.commit()
        self.db.refresh(db_room_config)
        return db_room_config

    def update_room_configuration(self, room_config_id: int, room_config_update: schemas.RoomConfigurationUpdate) -> Optional[models.RoomConfiguration]:
        db_room_config = self.get_room_configuration_by_id(room_config_id)
        if not db_room_config:
            return None

        update_data = room_config_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_room_config, key, value)

        self.db.add(db_room_config)
        self.db.commit()
        self.db.refresh(db_room_config)
        return db_room_config

    def delete_room_configuration(self, room_config_id: int) -> Optional[models.RoomConfiguration]:
        db_room_config = self.get_room_configuration_by_id(room_config_id)
        if not db_room_config:
            return None
        # Check for TourHotelAllocations associated with this room config.
        if db_room_config.tour_allocations:
            raise ValueError("Room configuration cannot be deleted as it is used in tour hotel allocations.")
        self.db.delete(db_room_config)
        self.db.commit()
        return db_room_config
