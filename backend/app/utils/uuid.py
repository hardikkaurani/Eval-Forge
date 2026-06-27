import uuid


def generate_uuid() -> str:
    """Generates a random UUID version 4 as a string."""
    return str(uuid.uuid4())


def is_valid_uuid(val: str) -> bool:
    """Validates if the given string is a valid UUID version 4.

    Args:
        val: The string to validate.

    Returns:
        bool: True if it is a valid UUIDv4, False otherwise.
    """
    try:
        uuid_obj = uuid.UUID(val, version=4)
        return str(uuid_obj) == val
    except ValueError:
        return False
