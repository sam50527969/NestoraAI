from pydantic import BaseModel
from typing import List


class DashboardKpis(BaseModel):
    new_leads: int
    pipeline_value: int
    tasks_today: int
    ai_score: int


class DashboardPipelineStage(BaseModel):
    label: str
    value: int


class DashboardSummary(BaseModel):
    kpis: DashboardKpis
    ai_brief: List[str]
    tasks: List[str]
    pipeline: List[DashboardPipelineStage]
    activity: List[str]