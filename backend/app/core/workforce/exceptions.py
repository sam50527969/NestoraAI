class WorkforceError(Exception):
    """Base workforce exception."""


class WorkerNotFoundError(WorkforceError):
    """Raised when a worker cannot be found."""


class WorkerExecutionError(WorkforceError):
    """Raised when a worker fails."""