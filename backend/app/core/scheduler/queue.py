from __future__ import annotations

import heapq

from app.core.scheduler.models import SchedulerTask
from app.core.scheduler.status import TaskStatus


class ExecutionQueue:
    """
    Priority queue used by the Executive Scheduler.

    Lower priority numbers execute first.

    Example:
        priority=1     Highest
        priority=50
        priority=100   Default
        priority=500
    """

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, SchedulerTask]] = []
        self._counter = 0

    def push(self, task: SchedulerTask) -> None:
        """
        Add a task to the execution queue.
        """
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.READY

        heapq.heappush(
            self._heap,
            (
                task.priority,
                self._counter,
                task,
            ),
        )

        self._counter += 1

    def pop(self) -> SchedulerTask | None:
        """
        Return the highest-priority task.

        Returns None when empty.
        """
        if not self._heap:
            return None

        _, _, task = heapq.heappop(self._heap)
        return task

    def peek(self) -> SchedulerTask | None:
        """
        Return the next task without removing it.
        """
        if not self._heap:
            return None

        return self._heap[0][2]

    def clear(self) -> None:
        self._heap.clear()
        self._counter = 0

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    def __len__(self) -> int:
        return len(self._heap)