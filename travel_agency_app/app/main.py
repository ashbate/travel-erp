from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import sqlalchemy # Required for db.execute with text

from app.core.config import settings
from app.database import engine, get_db
from app.models.base import Base # To create tables

# Function to create database tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Call this on startup.
# In production, you'd use Alembic for migrations.
create_db_and_tables()


@app.on_event("startup")
async def startup_event():
    print("Application startup complete.")
    # You can add other startup logic here, like connecting to external services

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown.")
    # Add shutdown logic here, like closing database connections if not handled by context managers

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}"}

# Example of using the DB session dependency
@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        db.execute(sqlalchemy.text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# Placeholder for including routers later
from app.routes import api_router_v1 # Import the main v1 router

app.include_router(api_router_v1, prefix="/api/v1") # Prefix all v1 routes with /api/v1
