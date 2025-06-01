import pytest
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app import schemas
from app.models import User # For assertions

# Test for creating a user
def test_create_user(db_session: Session):
    user_service = UserService(db_session)
    user_in = schemas.UserCreate(
        username="testuser",
        email="testuser@example.com",
        password="password123",
        full_name="Test User",
        role="agent"
    )
    created_user = user_service.create_user(user_create=user_in)

    assert created_user is not None
    assert created_user.username == "testuser"
    assert created_user.email == "testuser@example.com"
    assert created_user.full_name == "Test User"
    assert created_user.role == "agent"
    assert hasattr(created_user, 'hashed_password')
    assert created_user.hashed_password is not None
    # Verify password would require the security context, better tested in authenticate

    # Check it's in the DB
    db_user = db_session.query(User).filter(User.id == created_user.id).first()
    assert db_user is not None
    assert db_user.username == "testuser"

# Test for creating a duplicate username
def test_create_user_duplicate_username(db_session: Session):
    user_service = UserService(db_session)
    user_in1 = schemas.UserCreate(username="dupuser", email="dupuser1@example.com", password="pass")
    user_service.create_user(user_create=user_in1)

    user_in2 = schemas.UserCreate(username="dupuser", email="dupuser2@example.com", password="pass")
    with pytest.raises(ValueError) as excinfo:
        user_service.create_user(user_create=user_in2)
    assert "already exists" in str(excinfo.value)

# Test for authenticating a user
def test_authenticate_user_correct_password(db_session: Session):
    user_service = UserService(db_session)
    user_in = schemas.UserCreate(username="authuser", email="auth@example.com", password="correctpassword")
    user_service.create_user(user_create=user_in)

    authenticated_user = user_service.authenticate_user(username="authuser", password="correctpassword")
    assert authenticated_user is not None
    assert authenticated_user.username == "authuser"

# Test for authenticating with wrong password
def test_authenticate_user_wrong_password(db_session: Session):
    user_service = UserService(db_session)
    user_in = schemas.UserCreate(username="authwrong", email="authwrong@example.com", password="correctpassword")
    user_service.create_user(user_create=user_in)

    authenticated_user = user_service.authenticate_user(username="authwrong", password="wrongpassword")
    assert authenticated_user is None

# Test for authenticating a non-existent user
def test_authenticate_user_non_existent(db_session: Session):
    user_service = UserService(db_session)
    authenticated_user = user_service.authenticate_user(username="nouser", password="anypassword")
    assert authenticated_user is None
