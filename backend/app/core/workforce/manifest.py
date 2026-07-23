from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkerManifest:
    """
    Immutable description of an AI worker.
    """

    worker_id: str

    name: str

    description: str

    version: str

    capabilities: tuple[str, ...] = field(
        default_factory=tuple,
    )

    supported_executives: tuple[str, ...] = field(
        default_factory=tuple,
    )

    enabled: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "worker_id",
            self.worker_id.strip().lower(),
        )

    def supports(
        self,
        capability: str,
    ) -> bool:
        return (
            capability.strip().lower()
            in self.capabilities
        )

    def to_dict(self):
        return {
            "worker_id": self.worker_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": list(
                self.capabilities
            ),
            "supported_executives": list(
                self.supported_executives
            ),
            "enabled": self.enabled,
            "metadata": dict(
                self.metadata
            ),
        }