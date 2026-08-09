from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Any


@dataclass(slots=True)
class CompetitorRelevanceBreakdown:
    industry_match: int = 0
    category_match: int = 0
    keyword_match: int = 0
    location_match: int = 0
    exclusion_penalty: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompetitorRelevanceResult:
    business_name: str

    score: int
    included: bool

    reason: str

    breakdown: CompetitorRelevanceBreakdown = field(
        default_factory=CompetitorRelevanceBreakdown,
    )

    matched_terms: list[str] = field(
        default_factory=list,
    )

    excluded_terms: list[str] = field(
        default_factory=list,
    )

    confidence: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)