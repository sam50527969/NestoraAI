from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Any


@dataclass(slots=True)
class CompetitorScoreBreakdown:
    website: int = 0
    phone: int = 0
    email: int = 0
    social_presence: int = 0
    website_quality: int = 0
    reputation: int = 0
    seo: int = 0
    completeness: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompetitorStrengthScore:
    score: int
    label: str

    breakdown: CompetitorScoreBreakdown = field(
        default_factory=CompetitorScoreBreakdown,
    )

    confidence: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompetitorSwot:
    strengths: list[str] = field(
        default_factory=list,
    )

    weaknesses: list[str] = field(
        default_factory=list,
    )

    opportunities: list[str] = field(
        default_factory=list,
    )

    threats: list[str] = field(
        default_factory=list,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompetitorOpportunity:
    title: str
    description: str

    priority: str = "Medium"
    impact_score: int = 0

    category: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompetitorRecommendation:
    title: str
    action: str

    priority: str = "Medium"
    estimated_impact: str | None = None
    suggested_channel: str | None = None

    reasoning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompetitorIntelligenceReport:
    competitor_name: str

    strength: CompetitorStrengthScore

    swot: CompetitorSwot = field(
        default_factory=CompetitorSwot,
    )

    opportunities: list[
        CompetitorOpportunity
    ] = field(
        default_factory=list,
    )

    recommendations: list[
        CompetitorRecommendation
    ] = field(
        default_factory=list,
    )

    market_position: str | None = None
    digital_maturity: str | None = None

    summary: str | None = None

    confidence: int = 0

    raw_signals: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)