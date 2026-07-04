import abc
from typing import Any, Callable, Dict, Coroutine
from app.jobs.models.job import Job

# Signature of progress callback: async def progress_callback(percentage: float, step: str) -> None
ProgressCallback = Callable[[float, str], Coroutine[Any, Any, None]]

class BaseJobExecutor(abc.ABC):
    """Abstract base class for all background job executors."""

    @abc.abstractmethod
    async def execute(self, job: Job, progress_callback: ProgressCallback) -> Dict[str, Any]:
        """Executes the specific job logic.
        
        Args:
            job: The database Job document representing the execution metadata.
            progress_callback: An async function to invoke when updating execution progress.
            
        Returns:
            A dictionary containing execution outputs to be saved as the job result.
        """
        pass
