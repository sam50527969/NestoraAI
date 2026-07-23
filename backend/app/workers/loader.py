from __future__ import annotations

import importlib
import pkgutil

import app.workers
from app.core.workforce import (
    WorkerBase,
    workforce_registry,
)


class WorkerLoader:
    """
    Automatically discovers and registers worker packages.
    """

    def load(self) -> list[str]:
        loaded: list[str] = []

        for _, module_name, is_package in pkgutil.iter_modules(
            app.workers.__path__
        ):
            if not is_package:
                continue

            module = importlib.import_module(
                f"app.workers.{module_name}"
            )

            for obj in module.__dict__.values():
                if (
                    isinstance(obj, type)
                    and issubclass(obj, WorkerBase)
                    and obj is not WorkerBase
                ):
                    worker = obj()
                    workforce_registry.register(worker)

                    if worker.worker_id not in loaded:
                        loaded.append(worker.worker_id)

        return sorted(loaded)


worker_loader = WorkerLoader()