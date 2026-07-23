from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ExecutiveHealth(StrEnum):
    """
    Runtime health state of a registered executive.
    """

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ExecutiveManifest:
    """
    Immutable description of an executive available to Nestora.

    The registry uses this manifest to discover executives,
    route missions by capability, and expose executive metadata.
    """

    executive_id: str
    name: str
    description: str
    version: str

    capabilities: tuple[str, ...] = field(
        default_factory=tuple,
    )

    workers: tuple[str, ...] = field(
        default_factory=tuple,
    )

    tools: tuple[str, ...] = field(
        default_factory=tuple,
    )

    permissions: tuple[str, ...] = field(
        default_factory=tuple,
    )

    supported_missions: tuple[str, ...] = field(
        default_factory=tuple,
    )

    enabled: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        normalized_id = self.executive_id.strip().lower()

        if not normalized_id:
            raise ValueError(
                "executive_id cannot be empty."
            )

        if not self.name.strip():
            raise ValueError(
                "Executive name cannot be empty."
            )

        if not self.version.strip():
            raise ValueError(
                "Executive version cannot be empty."
            )

        object.__setattr__(
            self,
            "executive_id",
            normalized_id,
        )

        object.__setattr__(
            self,
            "name",
            self.name.strip(),
        )

        object.__setattr__(
            self,
            "description",
            self.description.strip(),
        )

        object.__setattr__(
            self,
            "version",
            self.version.strip(),
        )

        object.__setattr__(
            self,
            "capabilities",
            self._normalize_collection(
                self.capabilities,
            ),
        )

        object.__setattr__(
            self,
            "workers",
            self._normalize_collection(
                self.workers,
            ),
        )

        object.__setattr__(
            self,
            "tools",
            self._normalize_collection(
                self.tools,
            ),
        )

        object.__setattr__(
            self,
            "permissions",
            self._normalize_collection(
                self.permissions,
            ),
        )

        object.__setattr__(
            self,
            "supported_missions",
            self._normalize_collection(
                self.supported_missions,
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    def supports_capability(
        self,
        capability: str,
    ) -> bool:
        normalized_capability = (
            self._normalize_value(capability)
        )

        return normalized_capability in self.capabilities

    def supports_mission(
        self,
        mission_type: str,
    ) -> bool:
        normalized_mission = self._normalize_value(
            mission_type,
        )

        return (
            normalized_mission
            in self.supported_missions
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "executive_id": self.executive_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": list(
                self.capabilities,
            ),
            "workers": list(self.workers),
            "tools": list(self.tools),
            "permissions": list(
                self.permissions,
            ),
            "supported_missions": list(
                self.supported_missions,
            ),
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def _normalize_collection(
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        normalized_values = {
            ExecutiveManifest._normalize_value(
                value,
            )
            for value in values
            if value and value.strip()
        }

        return tuple(sorted(normalized_values))

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


@dataclass(slots=True)
class RegisteredExecutive:
    """
    Runtime record stored by the executive registry.
    """

    manifest: ExecutiveManifest

    handler: Any | None = None

    health: ExecutiveHealth = (
        ExecutiveHealth.UNKNOWN
    )

    health_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = self.manifest.to_dict()

        data.update(
            {
                "health": self.health.value,
                "health_message": (
                    self.health_message
                ),
                "handler_registered": (
                    self.handler is not None
                ),
            }
        )

        return data