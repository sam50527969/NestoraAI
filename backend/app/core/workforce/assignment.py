from __future__ import annotations

from typing import Any

from app.core.workforce.registry import (
    WorkforceRegistry,
    workforce_registry,
)
from app.core.workforce.result import WorkerResult
from app.core.workforce.task import WorkerTask


class WorkerAssignmentEngine:
    """
    Assigns tasks to registered Nestora AI workers.
    """

    def __init__(
        self,
        registry: WorkforceRegistry | None = None,
    ) -> None:
        self.registry = registry or workforce_registry

    async def assign(
        self,
        *,
        title: str,
        description: str = "",
        worker_id: str | None = None,
        capability: str | None = None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkerResult:
        """
        Assign work using either a worker ID or capability.
        """

        if bool(worker_id) == bool(capability):
            raise ValueError(
                "Provide exactly one of worker_id or capability."
            )

        if worker_id:
            worker = self.registry.get(worker_id)
        else:
            worker = self.registry.find_by_capability(
                capability or ""
            )

        task = WorkerTask(
            worker=worker.worker_id,
            title=title,
            description=description,
            payload=payload or {},
            metadata=metadata or {},
        )

        return await worker.run(task)


assignment_engine = WorkerAssignmentEngine()