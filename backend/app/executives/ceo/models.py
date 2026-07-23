from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


@dataclass(slots=True)
class ExecutiveRecommendation:
    title: str
    description: str
    department: str
    action_type: str

    priority_score: float
    impact_score: float
    urgency_score: float
    confidence_score: float

    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    status: RecommendationStatus = RecommendationStatus.PENDING

    estimated_value: float | None = None
    currency: str = "QAR"

    metadata: dict[str, Any] = field(default_factory=dict)

    def calculate_final_score(self) -> float:
        """
        Calculate the final recommendation score.

        Score weights:
        - Priority: 35%
        - Impact: 30%
        - Urgency: 20%
        - Confidence: 15%
        """
        final_score = (
            self.priority_score * 0.35
            + self.impact_score * 0.30
            + self.urgency_score * 0.20
            + self.confidence_score * 0.15
        )

        return round(final_score, 2)


@dataclass(slots=True)
class ExecutiveAction:
    title: str
    department: str
    instruction: str

    recommendation_score: float
    requires_approval: bool = True

    assigned_worker_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutivePlan:
    objective: str
    summary: str

    actions: list[ExecutiveAction] = field(default_factory=list)
    recommendations: list[ExecutiveRecommendation] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)