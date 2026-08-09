from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Any


@dataclass(slots=True)
class BusinessContact:
    phone: str | None = None
    email: str | None = None
    website: str | None = None


@dataclass(slots=True)
class BusinessLocation:
    address: str | None = None
    city: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass(slots=True)
class BusinessSocialProfiles:
    facebook: str | None = None
    instagram: str | None = None
    linkedin: str | None = None
    tiktok: str | None = None
    x: str | None = None


@dataclass(slots=True)
class BusinessReputation:
    rating: float | None = None
    review_count: int | None = None
    rating_scale: float = 5.0


@dataclass(slots=True)
class BusinessOpeningHours:
    open_now: bool | None = None
    weekday_text: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class BusinessIntelligenceProfile:
    name: str
    provider: str

    provider_id: str | None = None
    category: str | None = None

    contact: BusinessContact = field(
        default_factory=BusinessContact,
    )

    location: BusinessLocation = field(
        default_factory=BusinessLocation,
    )

    social_profiles: BusinessSocialProfiles = field(
        default_factory=BusinessSocialProfiles,
    )

    reputation: BusinessReputation = field(
        default_factory=BusinessReputation,
    )

    opening_hours: BusinessOpeningHours = field(
        default_factory=BusinessOpeningHours,
    )

    business_status: str | None = None
    verified: bool | None = None

    photos: list[str] = field(
        default_factory=list,
    )

    categories: list[str] = field(
        default_factory=list,
    )

    source_confidence: int = 0
    raw_data: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)