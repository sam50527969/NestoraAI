from __future__ import annotations

from collections import defaultdict, deque

from app.core.scheduler.models import SchedulerTask


class DependencyGraphError(Exception):
    """Base exception for dependency-graph failures."""


class DuplicateTaskError(DependencyGraphError):
    """Raised when a task with the same ID already exists."""


class UnknownDependencyError(DependencyGraphError):
    """Raised when a task references a dependency that does not exist."""


class CircularDependencyError(DependencyGraphError):
    """Raised when the workflow contains a dependency cycle."""


class DependencyGraph:
    """
    Directed acyclic graph for scheduler-task dependencies.

    Each task may depend on one or more other tasks. A task becomes
    eligible for execution only after all its dependencies complete.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, SchedulerTask] = {}
        self._dependents: dict[str, set[str]] = defaultdict(set)

    def add_task(self, task: SchedulerTask) -> SchedulerTask:
        """
        Add one task to the graph.

        Dependencies may be added before their referenced tasks, but the
        graph must be validated before execution.
        """
        if task.id in self._tasks:
            raise DuplicateTaskError(
                f"Task '{task.id}' already exists in the dependency graph."
            )

        self._tasks[task.id] = task

        for dependency_id in task.dependencies:
            self._dependents[dependency_id].add(task.id)

        return task

    def add_tasks(
        self,
        tasks: list[SchedulerTask],
    ) -> list[SchedulerTask]:
        """Add several tasks to the graph."""
        added_tasks: list[SchedulerTask] = []

        for task in tasks:
            added_tasks.append(self.add_task(task))

        return added_tasks

    def get_task(self, task_id: str) -> SchedulerTask | None:
        """Return a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[SchedulerTask]:
        """Return every task in insertion order."""
        return list(self._tasks.values())

    def get_dependencies(
        self,
        task_id: str,
    ) -> list[SchedulerTask]:
        """Return the direct dependencies of a task."""
        task = self._require_task(task_id)

        return [
            self._tasks[dependency_id]
            for dependency_id in task.dependencies
            if dependency_id in self._tasks
        ]

    def get_dependents(
        self,
        task_id: str,
    ) -> list[SchedulerTask]:
        """Return tasks that directly depend on the given task."""
        self._require_task(task_id)

        return [
            self._tasks[dependent_id]
            for dependent_id in self._dependents.get(task_id, set())
        ]

    def validate(self) -> None:
        """
        Validate that all dependencies exist and the graph has no cycles.
        """
        self._validate_dependencies()
        self.topological_order()

    def topological_order(self) -> list[SchedulerTask]:
        """
        Return tasks in dependency-safe execution order.

        Raises CircularDependencyError if the graph contains a cycle.
        """
        self._validate_dependencies()

        in_degree: dict[str, int] = {
            task_id: len(task.dependencies)
            for task_id, task in self._tasks.items()
        }

        ready = deque(
            task_id
            for task_id, degree in in_degree.items()
            if degree == 0
        )

        ordered_tasks: list[SchedulerTask] = []

        while ready:
            task_id = ready.popleft()
            ordered_tasks.append(self._tasks[task_id])

            for dependent_id in self._dependents.get(task_id, set()):
                in_degree[dependent_id] -= 1

                if in_degree[dependent_id] == 0:
                    ready.append(dependent_id)

        if len(ordered_tasks) != len(self._tasks):
            raise CircularDependencyError(
                "The scheduler workflow contains a circular dependency."
            )

        return ordered_tasks

    def clear(self) -> None:
        """Remove all tasks and dependency relationships."""
        self._tasks.clear()
        self._dependents.clear()

    def count(self) -> int:
        return len(self._tasks)

    def _validate_dependencies(self) -> None:
        for task in self._tasks.values():
            for dependency_id in task.dependencies:
                if dependency_id not in self._tasks:
                    raise UnknownDependencyError(
                        f"Task '{task.id}' depends on unknown task "
                        f"'{dependency_id}'."
                    )

                if dependency_id == task.id:
                    raise CircularDependencyError(
                        f"Task '{task.id}' cannot depend on itself."
                    )

    def _require_task(self, task_id: str) -> SchedulerTask:
        task = self._tasks.get(task_id)

        if task is None:
            raise KeyError(f"Task '{task_id}' was not found.")

        return task