from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Any


@dataclass(slots=True)
class BusinessAnalysisCompetitorSummary:
    name: str
    category: str | None = None
    location: str | None = None

    website: str | None = None
    phone: str | None = None
    email: str | None = None

    profile_strength: int = 0
    profile_strength_label: str | None = None

    market_position: str | None = None
    digital_maturity: str | None = None

    intelligence_confidence: int = 0

    competitor_intelligence: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class BusinessAnalysisMarketSummary:
    competitor_count: int = 0

    average_profile_strength: float = 0.0
    strongest_competitor: str | None = None
    weakest_competitor: str | None = None

    strong_competitors: int = 0
    moderate_competitors: int = 0
    weak_competitors: int = 0

    common_opportunities: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class BusinessAnalysisReport:
    business_name: str
    industry: str
    location: str

    objective: str
    timeline_days: int

    status: str = "completed"

    competitors: list[
        BusinessAnalysisCompetitorSummary
    ] = field(
        default_factory=list,
    )

    market_summary: BusinessAnalysisMarketSummary = field(
        default_factory=BusinessAnalysisMarketSummary,
    )

    growth_strategy: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    executive_summary: str | None = None

    confidence: int = 0

    errors: list[str] = field(
        default_factory=list,
    )

    raw_context: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)