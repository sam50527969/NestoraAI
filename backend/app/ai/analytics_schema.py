from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyticsKPI(BaseModel):
    name: str
    target: str
    measurement: str = ""
    frequency: str = ""


class AnalyticsInsight(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    recommended_action: str = ""


class AnalyticsReport(BaseModel):
    executive: str = "Analytics"
    task_title: str
    status: str = "completed"

    executive_summary: str

    measurement_strategy: str

    kpis: list[AnalyticsKPI] = Field(
        default_factory=list
    )

    dashboard_metrics: list[str] = Field(
        default_factory=list
    )

    insights: list[AnalyticsInsight] = Field(
        default_factory=list
    )

    optimization_actions: list[str] = Field(
        default_factory=list
    )

    reporting_cadence: list[str] = Field(
        default_factory=list
    )

    risks: list[str] = Field(
        default_factory=list
    )