import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Any
import os

# Set TESTING environment variable before importing app modules that depend on settings
os.environ['TESTING'] = 'true'

from app.main import app # Import your FastAPI app
from app.database import get_db # To override dependency
from app.models.base import Base # To create/drop tables
from app.core.config import settings # To get the TESTING_DATABASE_URL

# Use the testing database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db_once():
    """Create database tables once per test session."""
    # If the test DB file exists for SQLite, delete it to start fresh each session
    if "sqlite" in SQLALCHEMY_DATABASE_URL and os.path.exists(SQLALCHEMY_DATABASE_URL.split("///")[1]):
        os.remove(SQLALCHEMY_DATABASE_URL.split("///")[1])
    Base.metadata.create_all(bind=engine) # Create tables
    yield
    # Optional: Drop tables after tests if needed, or clean up file for SQLite
    # Base.metadata.drop_all(bind=engine)
    # if "sqlite" in SQLALCHEMY_DATABASE_URL and os.path.exists(SQLALCHEMY_DATABASE_URL.split("///")[1]):
    #     os.remove(SQLALCHEMY_DATABASE_URL.split("///")[1])

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, Any, None]:
    """Yield a database session for a test function, rolling back changes after."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session # Provide the session to the test

    session.close()
    transaction.rollback() # Rollback any changes made during the test
    connection.close()

@pytest.fixture(scope="function")
def test_client(db_session: Session) -> Generator[TestClient, Any, None]:
    """Fixture for the FastAPI TestClient, with overridden DB session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass # Session is managed by db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    del app.dependency_overrides[get_db] # Clean up override
