import os
from dotenv import load_dotenv
from typing import Optional # Ensure Optional is imported

load_dotenv() # Loads variables from .env file into environment

class Settings:
    PROJECT_NAME: str = "Travel Agency App API"
    PROJECT_VERSION: str = "0.1.0"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/travel_agency_db")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY") # Add this
    STRIPE_PUBLISHABLE_KEY: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY") # Add this
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET") # For webhook verification later

    # Example: "postgresql://postgres:mysecretpassword@db:5432/travel_agency_db" for docker
    # Or: "sqlite:///./travel_agency.db" for a local sqlite file

    # Add other configurations here, e.g., API keys, secrets
    # SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key")
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Example for local SQLite (simplest to start, no external DB needed):
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./travel_agency.db")

settings = Settings()
