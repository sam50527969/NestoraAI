from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class DepartmentState:
    department: str
    status: str = "unknown"
    health_score: float = 0.0
    summary: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CompanyState:
    captured_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    crm: DepartmentState | None = None
    marketing: DepartmentState | None = None
    sales: DepartmentState | None = None
    operations: DepartmentState | None = None
    finance: DepartmentState | None = None
    workforce: DepartmentState | None = None
    missions: DepartmentState | None = None
    website: DepartmentState | None = None
    memory: DepartmentState | None = None

    overall_health_score: float = 0.0
    strategic_objectives: list[str] = field(default_factory=list)
    critical_risks: list[str] = field(default_factory=list)
    major_opportunities: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def available_departments(self) -> list[DepartmentState]:
        departments = [
            self.crm,
            self.marketing,
            self.sales,
            self.operations,
            self.finance,
            self.workforce,
            self.missions,
            self.website,
            self.memory,
        ]

        return [
            department
            for department in departments
            if department is not None
        ]

    def calculate_overall_health(self) -> float:
        departments = self.available_departments()

        if not departments:
            self.overall_health_score = 0.0
            return self.overall_health_score

        total_score = sum(
            max(0.0, min(100.0, department.health_score))
            for department in departments
        )

        self.overall_health_score = round(
            total_score / len(departments),
            2,
        )

        return self.overall_health_score