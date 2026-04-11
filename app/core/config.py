# app/core/config.py
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Any


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Cinema Ticket API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3001",
        "http://localhost:8000",
    ]

    # Email
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 465
    EMAIL_USER: str
    EMAIL_APP_PASSWORD: str

    # Cache
    REDIS_URL: str = ""
    CACHE_DEFAULT_TTL: int = 300
    CACHE_HOME_TTL: int = 120

    # Cloudinary
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_UPLOAD_PRESET: str = "cinema"

    # App Settings
    DEBUG: bool = False

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }


# Global settings instance
settings = Settings()