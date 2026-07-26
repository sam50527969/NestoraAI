from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.execution.executive_registry import (
    ExecutiveNotFoundError,
    ExecutiveRegistry,
    executive_registry,
)
from app.core.scheduler.models import SchedulerTask


class ExecutiveDispatchError(Exception):
    """Base exception for executive dispatch failures."""


class UnsupportedExecutiveError(ExecutiveDispatchError):
    """Raised when a registered executive cannot execute tasks."""


@dataclass(slots=True)
class DispatchResult:
    """
    Structured outcome of dispatching one scheduler task.
    """

    task_id: str
    executor: str
    success: bool

    result: Any = None
    error: str | None = None

    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def execution_time_seconds(self) -> float:
        return max(
            0.0,
            (self.completed_at - self.started_at).total_seconds(),
        )


class ExecutiveDispatcher:
    """
    Resolves and invokes the executive assigned to a scheduler task.

    Supported executive interfaces, in order:

    1. executive.execute_task(task)
    2. executive.execute(payload)
    3. executive.run(payload)
    4. callable executive(payload)

    Both synchronous and asynchronous methods are supported.
    """

    def __init__(
        self,
        registry: ExecutiveRegistry | None = None,
    ) -> None:
        self.registry = registry or executive_registry

    async def dispatch(
        self,
        task: SchedulerTask,
    ) -> DispatchResult:
        started_at = datetime.utcnow()

        try:
            executive = self.registry.get(task.executor)
            result = await self._invoke(executive, task)

            return DispatchResult(
                task_id=task.id,
                executor=task.executor,
                success=True,
                result=result,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        except ExecutiveNotFoundError as exc:
            return DispatchResult(
                task_id=task.id,
                executor=task.executor,
                success=False,
                error=str(exc),
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        except Exception as exc:
            return DispatchResult(
                task_id=task.id,
                executor=task.executor,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    async def _invoke(
        self,
        executive: Any,
        task: SchedulerTask,
    ) -> Any:
        if hasattr(executive, "execute_task"):
            return await self._call(
                executive.execute_task,
                task,
            )

        if hasattr(executive, "execute"):
            return await self._call(
                executive.execute,
                task.payload,
            )

        if hasattr(executive, "run"):
            return await self._call(
                executive.run,
                task.payload,
            )

        if callable(executive):
            return await self._call(
                executive,
                task.payload,
            )

        raise UnsupportedExecutiveError(
            f"Executive '{task.executor}' does not provide "
            f"'execute_task', 'execute', 'run', or a callable interface."
        )

    @staticmethod
    async def _call(
        callable_object: Any,
        argument: Any,
    ) -> Any:
        result = callable_object(argument)

        if inspect.isawaitable(result):
            return await result

        return result


executive_dispatcher = ExecutiveDispatcher()