from app.core.exceptions import ValidationException
from app.utils.uuid import is_valid_uuid


def validate_uuid(val: str, field_name: str = "id") -> None:
    """Validates that a string matches UUIDv4 format, raising a ValidationException otherwise."""
    if not is_valid_uuid(val):
        raise ValidationException(
            message=f"Invalid UUID format for field: '{field_name}'",
            details={"field": field_name, "value": val},
        )


def validate_non_empty(val: str | None, field_name: str) -> str:
    """Validates that a string is not empty or whitespace, raising a ValidationException otherwise."""
    if not val or not val.strip():
        raise ValidationException(
            message=f"Field '{field_name}' cannot be empty or whitespace.",
            details={"field": field_name},
        )
    return val.strip()
