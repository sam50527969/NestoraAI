from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Any


@dataclass(slots=True)
class StrategyBudgetAllocation:
    channel: str
    amount: float
    percentage: float
    purpose: str


@dataclass(slots=True)
class StrategyBudget:
    monthly_budget: float
    currency: str = "QAR"

    allocations: list[
        StrategyBudgetAllocation
    ] = field(
        default_factory=list,
    )

    reserve_amount: float = 0.0


@dataclass(slots=True)
class StrategySeoAction:
    title: str
    description: str
    priority: str = "Medium"

    target_keywords: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class StrategySeoPlan:
    objective: str

    actions: list[
        StrategySeoAction
    ] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class StrategyAdCampaign:
    name: str
    channel: str
    objective: str

    daily_budget: float = 0.0

    audience: list[str] = field(
        default_factory=list,
    )

    keywords: list[str] = field(
        default_factory=list,
    )

    message: str | None = None


@dataclass(slots=True)
class StrategyContentItem:
    day: int
    channel: str
    content_type: str
    topic: str
    objective: str


@dataclass(slots=True)
class StrategyEmailStep:
    day: int
    subject: str
    purpose: str
    call_to_action: str


@dataclass(slots=True)
class StrategyTimelineAction:
    period: str
    title: str
    description: str
    owner: str = "Marketing Director"
    priority: str = "Medium"


@dataclass(slots=True)
class StrategyRoiForecast:
    monthly_investment: float
    currency: str = "QAR"

    estimated_leads: int = 0
    estimated_customers: int = 0
    estimated_revenue: float = 0.0

    estimated_roi_percent: float = 0.0

    assumptions: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class GrowthStrategyReport:
    business_name: str
    objective: str
    timeline_days: int

    budget: StrategyBudget

    seo_plan: StrategySeoPlan

    ad_campaigns: list[
        StrategyAdCampaign
    ] = field(
        default_factory=list,
    )

    content_calendar: list[
        StrategyContentItem
    ] = field(
        default_factory=list,
    )

    email_sequence: list[
        StrategyEmailStep
    ] = field(
        default_factory=list,
    )

    timeline: list[
        StrategyTimelineAction
    ] = field(
        default_factory=list,
    )

    roi_forecast: StrategyRoiForecast | None = None

    executive_summary: str | None = None

    priorities: list[str] = field(
        default_factory=list,
    )

    assumptions: list[str] = field(
        default_factory=list,
    )

    confidence: int = 0

    raw_context: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)