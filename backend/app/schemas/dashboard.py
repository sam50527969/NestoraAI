from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)


class DashboardKpis(BaseModel):
    total_leads: int = Field(ge=0)
    high_priority_leads: int = Field(
        ge=0
    )
    qualified_leads: int = Field(
        ge=0
    )
    won_leads: int = Field(ge=0)
    pipeline_value: int = Field(ge=0)
    ai_score: int = Field(
        ge=0,
        le=100,
    )


class DashboardPipelineStage(
    BaseModel
):
    label: str
    value: int = Field(ge=0)


class DashboardSummary(BaseModel):
    kpis: DashboardKpis
    ai_brief: list[str] = Field(
        default_factory=list
    )
    tasks: list[str] = Field(
        default_factory=list
    )
    pipeline: list[
        DashboardPipelineStage
    ] = Field(
        default_factory=list
    )
    activity: list[str] = Field(
        default_factory=list
    )