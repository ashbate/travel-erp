from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app import schemas
from app.core.security import get_password_hash, verify_password # Import hashing functions

class UserService:
    def __init__(self, db_session: Session):
        self.db = db_session

    # ... (get_user_by_id, get_user_by_username, get_user_by_email, get_all_users remain same) ...
    def get_user_by_id(self, user_id: int) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.email == email).first()

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create_user(self, user_create: schemas.UserCreate) -> models.User:
        if self.get_user_by_username(user_create.username):
            raise ValueError(f"User with username {user_create.username} already exists.")
        if self.get_user_by_email(user_create.email):
            raise ValueError(f"User with email {user_create.email} already exists.")

        hashed_password = get_password_hash(user_create.password)
        db_user = models.User(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password, # Store hashed password
            role=user_create.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username: str, password: str) -> Optional[models.User]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    # ... (update_user and delete_user remain same for now, but update might need password change logic later) ...
    def update_user(self, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != db_user.email:
            existing_user = self.get_user_by_email(update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"Another user with email {update_data['email']} already exists.")

        for key, value in update_data.items():
            setattr(db_user, key, value)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> Optional[models.User]:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        if db_user.tours_created:
            raise ValueError("User cannot be deleted as they have created tours. Reassign tours first.")
        self.db.delete(db_user)
        self.db.commit()
        return db_user
