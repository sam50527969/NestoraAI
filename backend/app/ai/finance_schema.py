from __future__ import annotations

from pydantic import BaseModel, Field


class FinanceAction(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    expected_impact: str = ""


class FinanceKPI(BaseModel):
    name: str
    target: str
    measurement: str = ""


class FinanceReport(BaseModel):
    executive: str = "Finance"
    task_title: str
    status: str = "completed"

    executive_summary: str
    financial_assessment: str

    budget_recommendations: list[str] = Field(
        default_factory=list
    )

    revenue_opportunities: list[str] = Field(
        default_factory=list
    )

    cost_controls: list[str] = Field(
        default_factory=list
    )

    cash_flow_actions: list[str] = Field(
        default_factory=list
    )

    recommended_actions: list[FinanceAction] = Field(
        default_factory=list
    )

    kpis: list[FinanceKPI] = Field(
        default_factory=list
    )

    risks: list[str] = Field(
        default_factory=list
    )
