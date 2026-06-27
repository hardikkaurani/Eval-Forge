from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """Returns the current UTC time as a timezone-aware datetime object."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime) -> str:
    """Formats a datetime object to ISO 8601 string format (e.g. YYYY-MM-DDTHH:MM:SS.ffffff+00:00)."""
    return dt.isoformat()
