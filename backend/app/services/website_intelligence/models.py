from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Any


@dataclass(slots=True)
class WebsiteContact:
    phones: list[str] = field(
        default_factory=list,
    )

    emails: list[str] = field(
        default_factory=list,
    )

    whatsapp_links: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class WebsiteSocialProfiles:
    facebook: str | None = None
    instagram: str | None = None
    linkedin: str | None = None
    tiktok: str | None = None
    x: str | None = None
    youtube: str | None = None


@dataclass(slots=True)
class WebsitePages:
    homepage: str | None = None
    contact: str | None = None
    about: str | None = None
    booking: str | None = None
    careers: str | None = None
    services: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class WebsiteSeoSignals:
    title: str | None = None
    meta_description: str | None = None
    meta_keywords: list[str] = field(
        default_factory=list,
    )

    canonical_url: str | None = None
    language: str | None = None

    has_robots_txt: bool | None = None
    has_sitemap: bool | None = None
    has_structured_data: bool | None = None

    headings: dict[str, list[str]] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class WebsiteTechnologySignals:
    cms: str | None = None
    analytics: list[str] = field(
        default_factory=list,
    )

    advertising: list[str] = field(
        default_factory=list,
    )

    chat_tools: list[str] = field(
        default_factory=list,
    )

    frameworks: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class WebsiteContentSignals:
    business_name: str | None = None
    summary: str | None = None

    services: list[str] = field(
        default_factory=list,
    )

    calls_to_action: list[str] = field(
        default_factory=list,
    )

    languages: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class WebsiteIntelligenceProfile:
    website: str
    status: str

    final_url: str | None = None
    status_code: int | None = None

    contact: WebsiteContact = field(
        default_factory=WebsiteContact,
    )

    social_profiles: WebsiteSocialProfiles = field(
        default_factory=WebsiteSocialProfiles,
    )

    pages: WebsitePages = field(
        default_factory=WebsitePages,
    )

    seo: WebsiteSeoSignals = field(
        default_factory=WebsiteSeoSignals,
    )

    technologies: WebsiteTechnologySignals = field(
        default_factory=WebsiteTechnologySignals,
    )

    content: WebsiteContentSignals = field(
        default_factory=WebsiteContentSignals,
    )

    response_time_ms: int | None = None
    is_https: bool = False
    is_mobile_friendly: bool | None = None

    confidence: int = 0
    errors: list[str] = field(
        default_factory=list,
    )

    raw_data: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)