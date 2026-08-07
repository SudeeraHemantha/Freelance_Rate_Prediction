import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Freelance Rate & Demand Predictor API"
    ENV: str = "development"
    DEBUG: bool = True
    
    # Database Settings
    # Default to our custom user-space PostgreSQL instance on port 5433
    DATABASE_URL: str = Field(
        default="postgresql://postgres@localhost:5433/freelance_predictor",
        validation_alias="DATABASE_URL"
    )

    # Redis Settings for Caching and Rate Limiting
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )

    # Security Settings
    API_KEY: str = Field(
        default="freelance_sec_demo_key_2026",
        validation_alias="API_KEY"
    )
    JWT_SECRET: str = Field(
        default="freelance_predictor_enterprise_jwt_secret_key_2026",
        validation_alias="JWT_SECRET"
    )
    JWT_ALGORITHM: str = "HS256"

    # Rate Limiting Settings
    RATE_LIMIT_PER_MINUTE: str = "20/minute"

    # CORS Settings
    CORS_ORIGINS: str = Field(
        default="*",
        validation_alias="CORS_ORIGINS"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

