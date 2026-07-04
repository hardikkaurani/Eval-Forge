class JobException(Exception):
    """Base exception for all job execution platform exceptions."""
    pass

class JobNotFoundException(JobException):
    def __init__(self, job_id: str):
        super().__init__(f"Job with ID '{job_id}' not found.")
        self.job_id = job_id

class InvalidStatusTransitionException(JobException):
    def __init__(self, job_id: str, current_status: str, target_status: str):
        super().__init__(
            f"Invalid transition for Job '{job_id}': cannot move from '{current_status}' to '{target_status}'."
        )
        self.job_id = job_id
        self.current_status = current_status
        self.target_status = target_status

class QueueNotFoundException(JobException):
    def __init__(self, queue_name: str):
        super().__init__(f"Queue with name '{queue_name}' not found.")
        self.queue_name = queue_name

class WorkerNotFoundException(JobException):
    def __init__(self, worker_id: str):
        super().__init__(f"Worker with ID '{worker_id}' not found.")
        self.worker_id = worker_id
