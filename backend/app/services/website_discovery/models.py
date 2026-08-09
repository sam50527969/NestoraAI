from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Any


@dataclass(slots=True)
class WebsiteCandidate:
    url: str
    provider: str

    title: str | None = None
    snippet: str | None = None

    business_name_match: int = 0
    location_match: int = 0
    domain_match: int = 0

    confidence: int = 0
    verified: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class WebsiteDiscoveryResult:
    business_name: str
    location: str

    website: str | None = None
    status: str = "not_found"

    provider: str | None = None
    confidence: int = 0

    candidates: list[WebsiteCandidate] = field(
        default_factory=list,
    )

    errors: list[str] = field(
        default_factory=list,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)