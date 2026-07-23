from __future__ import annotations

from threading import RLock
from typing import Any

from app.core.registry.models import (
    ExecutiveHealth,
    ExecutiveManifest,
    RegisteredExecutive,
)


class ExecutiveRegistryError(Exception):
    """
    Base exception for executive registry errors.
    """


class ExecutiveAlreadyRegisteredError(
    ExecutiveRegistryError
):
    """
    Raised when an executive ID is registered twice.
    """


class ExecutiveNotFoundError(
    ExecutiveRegistryError
):
    """
    Raised when an executive cannot be found.
    """


class ExecutiveRegistry:
    """
    Thread-safe registry for Nestora AI executives.

    Executives can be located by ID, capability,
    mission type, or runtime availability.
    """

    def __init__(self) -> None:
        self._executives: dict[
            str,
            RegisteredExecutive,
        ] = {}

        self._lock = RLock()

    def register(
        self,
        manifest: ExecutiveManifest,
        *,
        handler: Any | None = None,
        replace: bool = False,
    ) -> RegisteredExecutive:
        executive_id = manifest.executive_id

        with self._lock:
            if (
                executive_id in self._executives
                and not replace
            ):
                raise (
                    ExecutiveAlreadyRegisteredError(
                        "Executive already registered: "
                        f"{executive_id}"
                    )
                )

            registered = RegisteredExecutive(
                manifest=manifest,
                handler=handler,
                health=ExecutiveHealth.UNKNOWN,
            )

            self._executives[
                executive_id
            ] = registered

            return registered

    def unregister(
        self,
        executive_id: str,
    ) -> bool:
        normalized_id = self._normalize_value(
            executive_id,
        )

        with self._lock:
            return (
                self._executives.pop(
                    normalized_id,
                    None,
                )
                is not None
            )

    def get(
        self,
        executive_id: str,
    ) -> RegisteredExecutive:
        normalized_id = self._normalize_value(
            executive_id,
        )

        with self._lock:
            registered = self._executives.get(
                normalized_id,
            )

        if registered is None:
            raise ExecutiveNotFoundError(
                "Executive not found: "
                f"{normalized_id}"
            )

        return registered

    def get_optional(
        self,
        executive_id: str,
    ) -> RegisteredExecutive | None:
        normalized_id = self._normalize_value(
            executive_id,
        )

        with self._lock:
            return self._executives.get(
                normalized_id,
            )

    def list_all(
        self,
        *,
        enabled_only: bool = False,
    ) -> list[RegisteredExecutive]:
        with self._lock:
            executives = list(
                self._executives.values(),
            )

        if enabled_only:
            executives = [
                executive
                for executive in executives
                if executive.manifest.enabled
            ]

        return sorted(
            executives,
            key=lambda item: item.manifest.name,
        )

    def find_by_capability(
        self,
        capability: str,
        *,
        enabled_only: bool = True,
    ) -> list[RegisteredExecutive]:
        normalized_capability = (
            self._normalize_value(capability)
        )

        executives = self.list_all(
            enabled_only=enabled_only,
        )

        return [
            executive
            for executive in executives
            if executive.manifest
            .supports_capability(
                normalized_capability,
            )
        ]

    def find_by_mission(
        self,
        mission_type: str,
        *,
        enabled_only: bool = True,
    ) -> list[RegisteredExecutive]:
        normalized_mission = (
            self._normalize_value(mission_type)
        )

        executives = self.list_all(
            enabled_only=enabled_only,
        )

        return [
            executive
            for executive in executives
            if executive.manifest
            .supports_mission(
                normalized_mission,
            )
        ]

    def update_health(
        self,
        executive_id: str,
        health: ExecutiveHealth,
        *,
        message: str | None = None,
    ) -> RegisteredExecutive:
        with self._lock:
            registered = self.get(
                executive_id,
            )

            registered.health = health
            registered.health_message = (
                message.strip()
                if message
                else None
            )

            return registered

    def resolve_handler(
        self,
        executive_id: str,
    ) -> Any:
        registered = self.get(executive_id)

        if registered.handler is None:
            raise ExecutiveRegistryError(
                "No runtime handler registered for "
                f"executive: {executive_id}"
            )

        if not registered.manifest.enabled:
            raise ExecutiveRegistryError(
                "Executive is disabled: "
                f"{executive_id}"
            )

        if (
            registered.health
            == ExecutiveHealth.UNAVAILABLE
        ):
            raise ExecutiveRegistryError(
                "Executive is unavailable: "
                f"{executive_id}"
            )

        return registered.handler

    def count(
        self,
        *,
        enabled_only: bool = False,
    ) -> int:
        return len(
            self.list_all(
                enabled_only=enabled_only,
            )
        )

    def clear(self) -> None:
        with self._lock:
            self._executives.clear()

    def to_dict(
        self,
        *,
        enabled_only: bool = False,
    ) -> list[dict[str, Any]]:
        return [
            executive.to_dict()
            for executive in self.list_all(
                enabled_only=enabled_only,
            )
        ]

    @staticmethod
    def _normalize_value(
        value: str,
    ) -> str:
        return (
            value.strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )


executive_registry = ExecutiveRegistry()