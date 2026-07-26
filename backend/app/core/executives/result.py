from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.executives.artifact import ExecutiveArtifact


@dataclass(slots=True)
class ExecutiveResult:
    """
    Standard response returned by every Nestora executive.
    """

    success: bool = True

    summary: str = ""

    data: dict[str, Any] = field(
        default_factory=dict,
    )

    warnings: list[str] = field(
        default_factory=list,
    )

    recommendations: list[str] = field(
        default_factory=list,
    )

    metrics: dict[str, Any] = field(
        default_factory=dict,
    )

    artifacts: list[ExecutiveArtifact] = field(
        default_factory=list,
    )

    next_actions: list[str] = field(
        default_factory=list,
    )

    confidence: float | None = None

    executive_name: str | None = None

    mission_id: str | None = None

    workflow_id: str | None = None

    task_id: str | None = None

    started_at: datetime | None = None

    completed_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    @property
    def artifact_count(self) -> int:
        return len(self.artifacts)

    @property
    def duration_seconds(self) -> float | None:
        if self.started_at is None:
            return None

        return max(
            0.0,
            (
                self.completed_at
                - self.started_at
            ).total_seconds(),
        )

    def validate_confidence(self) -> None:
        """
        Ensure confidence is expressed as a value from 0.0 to 1.0.
        """

        if self.confidence is None:
            return

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Confidence must be between 0.0 and 1.0."
            )