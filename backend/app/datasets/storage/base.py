from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorage(ABC):
    """Abstract interface defining required methods for file storage backends."""

    @abstractmethod
    async def save(self, file_path: str, content: BinaryIO) -> str:
        """Saves file binary content and returns the absolute/virtual path/identifier."""
        pass

    @abstractmethod
    async def read(self, file_path: str) -> BinaryIO:
        """Reads file binary content."""
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """Deletes file from storage."""
        pass

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """Generates a downloadable/accessible URL for the file."""
        pass
