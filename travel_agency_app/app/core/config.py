import os
from dotenv import load_dotenv
from typing import Optional # Ensure Optional is imported
from datetime import timedelta # Import timedelta

load_dotenv() # Loads variables from .env file into environment

class Settings:
    PROJECT_NAME: str = "Travel Agency App API"
    PROJECT_VERSION: str = "0.1.0"

    # Database URL: Use TESTING_DATABASE_URL if 'TESTING' env var is set, else regular DATABASE_URL
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    PRIMARY_DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/travel_agency_db")
    TESTING_DATABASE_URL: str = os.getenv("TESTING_DATABASE_URL", "sqlite:///./test_travel_agency.db")

    @property
    def DATABASE_URL(self) -> str:
        return self.TESTING_DATABASE_URL if self.TESTING else self.PRIMARY_DATABASE_URL

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    # ... (Stripe and JWT settings remain the same)
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_and_long_random_string_for_jwt") # IMPORTANT: Use a strong random key in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Example: "postgresql://postgres:mysecretpassword@db:5432/travel_agency_db" for docker
    # Or: "sqlite:///./travel_agency.db" for a local sqlite file

    # Add other configurations here, e.g., API keys, secrets
    # SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key")
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Example for local SQLite (simplest to start, no external DB needed):
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./travel_agency.db")

settings = Settings()
