from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app import schemas

class GuestService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_guest_by_id(self, guest_id: int) -> Optional[models.Guest]:
        return self.db.query(models.Guest).filter(models.Guest.id == guest_id).first()

    def get_guest_by_email(self, email: str) -> Optional[models.Guest]:
        return self.db.query(models.Guest).filter(models.Guest.email == email).first()

    def get_all_guests(self, skip: int = 0, limit: int = 100) -> List[models.Guest]:
        return self.db.query(models.Guest).offset(skip).limit(limit).all()

    def create_guest(self, guest_create: schemas.GuestCreate) -> models.Guest:
        # Check if guest with this email already exists
        existing_guest = self.get_guest_by_email(guest_create.email)
        if existing_guest:
            raise ValueError(f"Guest with email {guest_create.email} already exists.")

        db_guest = models.Guest(**guest_create.model_dump())
        self.db.add(db_guest)
        self.db.commit()
        self.db.refresh(db_guest)
        return db_guest

    def update_guest(self, guest_id: int, guest_update: schemas.GuestUpdate) -> Optional[models.Guest]:
        db_guest = self.get_guest_by_id(guest_id)
        if not db_guest:
            return None

        update_data = guest_update.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != db_guest.email:
            existing_guest = self.get_guest_by_email(update_data["email"])
            if existing_guest and existing_guest.id != guest_id:
                raise ValueError(f"Another guest with email {update_data['email']} already exists.")

        for key, value in update_data.items():
            setattr(db_guest, key, value)

        self.db.add(db_guest)
        self.db.commit()
        self.db.refresh(db_guest)
        return db_guest

    def delete_guest(self, guest_id: int) -> Optional[models.Guest]:
        db_guest = self.get_guest_by_id(guest_id)
        if not db_guest:
            return None
        # Consider if there are associated bookings. For now, direct delete.
        # Add logic to check for active bookings before deleting or handle it via DB constraints.
        self.db.delete(db_guest)
        self.db.commit()
        return db_guest
