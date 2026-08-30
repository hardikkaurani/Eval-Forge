from app.core.exceptions import EvalForgeException


class DatasetException(EvalForgeException):
    """Base exception for all dataset and benchmark-related errors."""

    pass


class DatasetNotFoundException(DatasetException):
    """Raised when a dataset or version is not found."""

    def __init__(self, dataset_id: str, version: str | None = None):
        if version:
            message = f"Dataset '{dataset_id}' with version '{version}' not found."
        else:
            message = f"Dataset '{dataset_id}' not found."
        super().__init__(message=message, status_code=404)


class DatasetValidationException(DatasetException):
    """Raised when dataset validation fails."""

    def __init__(self, message: str, details: dict | list | None = None):
        super().__init__(message=message, status_code=400, details=details)


class InvalidDatasetFormatException(DatasetException):
    """Raised when an unsupported or malformed dataset file format is processed."""

    def __init__(self, file_format: str, details: str | None = None):
        message = f"Unsupported or malformed dataset format: '{file_format}'."
        if details:
            message += f" Details: {details}"
        super().__init__(message=message, status_code=400)


class BenchmarkSuiteNotFoundException(DatasetException):
    """Raised when a benchmark suite is not found."""

    def __init__(self, suite_id: str, message: str | None = None):
        msg = message or f"Benchmark suite '{suite_id}' not found."
        super().__init__(message=msg, status_code=404)


class ExperimentNotFoundException(DatasetException):
    """Raised when an experiment run is not found."""

    def __init__(self, experiment_id: str, message: str | None = None):
        msg = message or f"Experiment '{experiment_id}' not found."
        super().__init__(message=msg, status_code=404)


class StorageException(DatasetException):
    """Raised when file storage operations fail."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=500)
