from __future__ import annotations

from pydantic import BaseModel, Field


class SalesAction(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    expected_impact: str = ""


class SalesStage(BaseModel):
    stage: str
    objective: str
    actions: list[str] = Field(default_factory=list)


class SalesKPI(BaseModel):
    name: str
    target: str
    measurement: str = ""


class SalesReport(BaseModel):
    executive: str = "Sales"
    task_title: str
    status: str = "completed"

    executive_summary: str

    sales_strategy: str

    target_customer_profile: str

    sales_process: list[SalesStage] = Field(
        default_factory=list
    )

    objection_handling: list[str] = Field(
        default_factory=list
    )

    outreach_script: list[str] = Field(
        default_factory=list
    )

    recommended_actions: list[SalesAction] = Field(
        default_factory=list
    )

    kpis: list[SalesKPI] = Field(
        default_factory=list
    )

    risks: list[str] = Field(
        default_factory=list
    )