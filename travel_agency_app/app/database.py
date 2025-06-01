from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Will create this shortly

# Define DATABASE_URL based on your config settings
#SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host:port/database"
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Placeholder for Base from models to create tables (optional here, usually in main or a script)
# from app.models.base import Base
# def create_tables():
#     Base.metadata.create_all(bind=engine)
