import os
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine environment to load corresponding .env file
# Order of precedence: environment variables > .env.{APP_ENV} > .env > .env.example
APP_ENV = os.getenv("APP_ENV", "development").lower()

env_files = [".env.example"]
if os.path.exists(".env"):
    env_files.append(".env")
if os.path.exists(f".env.{APP_ENV}"):
    env_files.append(f".env.{APP_ENV}")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=tuple(env_files),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core Application Settings
    APP_NAME: str = "EvalForge API"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = Field(5432, ge=1, le=65535)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = SecretStr("postgres_password")
    POSTGRES_DB: str = "evalforge"
    DATABASE_URL: str | None = None

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(6379, ge=1, le=65535)
    REDIS_DB: int = Field(0, ge=0)
    REDIS_URL: str | None = None

    # Logging Configuration
    LOG_LEVEL: Literal["debug", "info", "warning", "error", "critical"] = "info"
    JSON_LOGS: bool = False

    # Security Configuration
    SECRET_KEY: SecretStr = SecretStr("dev-secret-key-evalforge-placeholder")
    CORS_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]

    # LLM Provider API Keys
    OPENAI_API_KEY: SecretStr | None = None
    GEMINI_API_KEY: SecretStr | None = None
    ANTHROPIC_API_KEY: SecretStr | None = None
    COHERE_API_KEY: SecretStr | None = None

    @field_validator("APP_ENV", mode="before")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        if isinstance(v, str):
            return v.lower()
        return v

    @property
    def get_database_url(self) -> str:
        """Constructs or retrieves the database connection string.

        Supports dynamic replacement of environment variables in DATABASE_URL if
        they are in the format ${VAR}.
        """
        if self.DATABASE_URL:
            db_url = self.DATABASE_URL
            if "${" in db_url:
                db_url = db_url.replace("${POSTGRES_USER}", self.POSTGRES_USER)
                db_url = db_url.replace(
                    "${POSTGRES_PASSWORD}", self.POSTGRES_PASSWORD.get_secret_value()
                )
                db_url = db_url.replace("${POSTGRES_SERVER}", self.POSTGRES_SERVER)
                db_url = db_url.replace("${POSTGRES_PORT}", str(self.POSTGRES_PORT))
                db_url = db_url.replace("${POSTGRES_DB}", self.POSTGRES_DB)
            return db_url

        password = self.POSTGRES_PASSWORD.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def get_redis_url(self) -> str:
        """Constructs or retrieves the Redis connection string."""
        if self.REDIS_URL:
            redis_url = self.REDIS_URL
            if "${" in redis_url:
                redis_url = redis_url.replace("${REDIS_HOST}", self.REDIS_HOST)
                redis_url = redis_url.replace("${REDIS_PORT}", str(self.REDIS_PORT))
                redis_url = redis_url.replace("${REDIS_DB}", str(self.REDIS_DB))
            return redis_url
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Initialize the settings instance
settings = Settings()
