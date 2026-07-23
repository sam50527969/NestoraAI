from __future__ import annotations

from app.core.workforce.exceptions import WorkerNotFoundError
from app.core.workforce.worker import WorkerBase


class WorkforceRegistry:
    """
    Registry of available Nestora AI workers.
    """

    def __init__(self) -> None:
        self._workers: dict[str, WorkerBase] = {}

    def register(
        self,
        worker: WorkerBase,
    ) -> None:
        worker_id = worker.worker_id.strip().lower()

        if not worker_id:
            raise ValueError(
                "Worker must define a non-empty worker_id."
            )

        self._workers[worker_id] = worker

    def register_many(
        self,
        workers: list[WorkerBase],
    ) -> None:
        for worker in workers:
            self.register(worker)

    def get(
        self,
        worker_id: str,
    ) -> WorkerBase:
        normalized_id = worker_id.strip().lower()

        worker = self._workers.get(normalized_id)

        if worker is None:
            raise WorkerNotFoundError(
                f"Worker '{normalized_id}' was not found."
            )

        return worker

    def find_by_capability(
        self,
        capability: str,
    ) -> WorkerBase:
        normalized_capability = capability.strip().lower()

        for worker in self._workers.values():
            manifest = getattr(worker, "manifest", None)

            if manifest is None or not manifest.enabled:
                continue

            if manifest.supports(normalized_capability):
                return worker

        raise WorkerNotFoundError(
            "No enabled worker supports capability "
            f"'{normalized_capability}'."
        )

    def find_all_by_capability(
        self,
        capability: str,
    ) -> list[WorkerBase]:
        normalized_capability = capability.strip().lower()
        matching_workers: list[WorkerBase] = []

        for worker in self._workers.values():
            manifest = getattr(worker, "manifest", None)

            if manifest is None or not manifest.enabled:
                continue

            if manifest.supports(normalized_capability):
                matching_workers.append(worker)

        return matching_workers

    def list_workers(self) -> list[str]:
        return sorted(self._workers.keys())

    def count(self) -> int:
        return len(self._workers)

    def clear(self) -> None:
        self._workers.clear()


workforce_registry = WorkforceRegistry()