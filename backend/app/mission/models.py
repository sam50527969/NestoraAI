from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MissionTask:
    title: str
    description: str
    executive: str
    priority: str = "medium"
    estimated_value: float | None = None
    depends_on: str | None = None


@dataclass(slots=True)
class MissionPlan:
    title: str
    objective: str
    description: str
    priority: str
    estimated_value: float | None
    expected_roi: float | None

    strategy_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    tasks: list[MissionTask] = field(default_factory=list)