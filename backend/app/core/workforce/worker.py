from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.workforce.result import WorkerResult
from app.core.workforce.task import WorkerTask


class WorkerBase(ABC):
    """
    Base class for every Nestora AI Worker.
    """

    worker_id: str = ""

    name: str = ""

    description: str = ""

    async def run(
        self,
        task: WorkerTask,
    ) -> WorkerResult:
        """
        Execute a task assigned by an Executive.
        """

        await self.before_execute(task)

        result = await self.execute(task)

        await self.after_execute(
            task,
            result,
        )

        return result

    async def before_execute(
        self,
        task: WorkerTask,
    ) -> None:
        """
        Optional hook executed before work begins.
        """
        return None

    @abstractmethod
    async def execute(
        self,
        task: WorkerTask,
    ) -> WorkerResult:
        """
        Worker implementation.
        """

    async def after_execute(
        self,
        task: WorkerTask,
        result: WorkerResult,
    ) -> None:
        """
        Optional hook after execution.
        """
        return None