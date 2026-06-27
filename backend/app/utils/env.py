from app.config.config import settings


def is_development() -> bool:
    """Checks if the application is running in development mode."""
    return settings.APP_ENV == "development"


def is_testing() -> bool:
    """Checks if the application is running in testing mode."""
    return settings.APP_ENV == "testing"


def is_production() -> bool:
    """Checks if the application is running in production mode."""
    return settings.APP_ENV == "production"
