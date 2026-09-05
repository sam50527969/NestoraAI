from __future__ import annotations

from pydantic import BaseModel, Field


class OperationsAction(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    expected_impact: str = ""


class OperationsKPI(BaseModel):
    name: str
    target: str
    measurement: str = ""


class OperationsReport(BaseModel):
    executive: str = "Operations"
    task_title: str
    status: str = "completed"

    executive_summary: str
    operational_assessment: str

    workflow_recommendations: list[str] = Field(
        default_factory=list
    )

    capacity_actions: list[str] = Field(
        default_factory=list
    )

    process_improvements: list[str] = Field(
        default_factory=list
    )

    recommended_actions: list[OperationsAction] = Field(
        default_factory=list
    )

    kpis: list[OperationsKPI] = Field(
        default_factory=list
    )

    bottlenecks: list[str] = Field(
        default_factory=list
    )

    risks: list[str] = Field(
        default_factory=list
    )
