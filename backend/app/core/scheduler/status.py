from enum import Enum


class TaskStatus(str, Enum):
    """
    Lifecycle states for scheduler tasks.
    """

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        """
        Return True when the task cannot continue executing.
        """
        return self in {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        }

    @property
    def is_active(self) -> bool:
        """
        Return True when the task is currently part of execution.
        """
        return self in {
            TaskStatus.READY,
            TaskStatus.RUNNING,
            TaskStatus.RETRYING,
        }