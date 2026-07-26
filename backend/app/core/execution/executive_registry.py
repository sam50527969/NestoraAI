from __future__ import annotations

from typing import Any


class ExecutiveAlreadyRegisteredError(Exception):
    """Raised when attempting to register an executive twice."""


class ExecutiveNotFoundError(Exception):
    """Raised when an executive cannot be found."""


class ExecutiveRegistry:
    """
    Central registry for all business executives.

    Executives register themselves here so the dispatcher
    can discover and execute them dynamically.
    """

    def __init__(self) -> None:
        self._executives: dict[str, Any] = {}

    def register(self, name: str, executive: Any) -> None:
        key = self._normalize(name)

        if key in self._executives:
            raise ExecutiveAlreadyRegisteredError(
                f"Executive '{key}' is already registered."
            )

        self._executives[key] = executive

    def unregister(self, name: str) -> None:
        self._executives.pop(self._normalize(name), None)

    def get(self, name: str) -> Any:
        key = self._normalize(name)

        executive = self._executives.get(key)

        if executive is None:
            raise ExecutiveNotFoundError(
                f"Executive '{key}' is not registered."
            )

        return executive

    def exists(self, name: str) -> bool:
        return self._normalize(name) in self._executives

    def list(self) -> list[str]:
        return sorted(self._executives.keys())

    def clear(self) -> None:
        self._executives.clear()

    @staticmethod
    def _normalize(name: str) -> str:
        return (
            name.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )


executive_registry = ExecutiveRegistry()