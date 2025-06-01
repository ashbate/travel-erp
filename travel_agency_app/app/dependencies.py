from sqlalchemy.orm import Session
from fastapi import Depends # Ensure Depends is imported
from app.database import SessionLocal # Corrected: get_db is already a dependency injector

def get_db_session(): # Renamed to avoid confusion with get_db in database.py
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# The get_db function in database.py is already designed as a FastAPI dependency.
# So, in your route files, you'll use:
# from app.database import get_db
# from sqlalchemy.orm import Session
# from fastapi import APIRouter, Depends
# router = APIRouter()
# @router.get("/")
# async def some_route(db: Session = Depends(get_db)):
#     # ... use db session ...

# If you wanted a different dependency structure, you could define it here.
# For now, get_db from database.py is the primary way to inject sessions.
# This dependencies.py file can be used for other types of dependencies later,
# such as authentication.
