from __future__ import annotations

from pydantic import BaseModel, Field


class CustomerSuccessAction(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    expected_impact: str = ""


class RetentionStrategy(BaseModel):
    objective: str
    target_customers: str
    engagement_plan: list[str] = Field(
        default_factory=list
    )
    retention_actions: list[str] = Field(
        default_factory=list
    )
    follow_up_plan: list[str] = Field(
        default_factory=list
    )


class CustomerSuccessKPI(BaseModel):
    name: str
    target: str
    measurement: str = ""


class CustomerSuccessReport(BaseModel):
    executive: str = "Customer Success"
    task_title: str
    status: str = "completed"

    executive_summary: str

    retention_strategy: RetentionStrategy

    recommended_actions: list[
        CustomerSuccessAction
    ] = Field(default_factory=list)

    customer_messages: list[str] = Field(
        default_factory=list
    )

    kpis: list[CustomerSuccessKPI] = Field(
        default_factory=list
    )

    risks: list[str] = Field(default_factory=list)