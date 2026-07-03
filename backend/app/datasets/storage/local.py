import os
import shutil
from io import BytesIO
from typing import BinaryIO

from app.datasets.exceptions.exceptions import StorageException
from app.datasets.storage.base import BaseStorage


class LocalStorage(BaseStorage):
    """Local filesystem implementation of the BaseStorage class."""

    def __init__(self, base_directory: str = "datasets"):
        self.base_directory = base_directory
        os.makedirs(self.base_directory, exist_ok=True)

    async def save(self, file_path: str, content: BinaryIO) -> str:
        full_path = os.path.join(self.base_directory, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            with open(full_path, "wb") as f:
                shutil.copyfileobj(content, f)
        except Exception as e:
            raise StorageException(f"Failed to save file locally at '{file_path}': {str(e)}")

        return full_path

    async def read(self, file_path: str) -> BinaryIO:
        full_path = os.path.join(self.base_directory, file_path)
        if not os.path.exists(full_path):
            raise StorageException(f"File not found locally at '{file_path}'")

        try:
            with open(full_path, "rb") as f:
                return BytesIO(f.read())
        except Exception as e:
            raise StorageException(f"Failed to read file locally at '{file_path}': {str(e)}")

    async def delete(self, file_path: str) -> bool:
        full_path = os.path.join(self.base_directory, file_path)
        if not os.path.exists(full_path):
            return False

        try:
            os.remove(full_path)
            return True
        except Exception as e:
            raise StorageException(f"Failed to delete file locally at '{file_path}': {str(e)}")

    def get_url(self, file_path: str) -> str:
        # Returns a relative path suitable for download endpoints
        return f"/api/v1/datasets/download/{file_path}"
