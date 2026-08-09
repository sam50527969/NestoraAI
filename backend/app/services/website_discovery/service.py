from __future__ import annotations

from typing import Iterable
from urllib.parse import urlparse

import httpx

from app.services.website_discovery.models import (
    WebsiteCandidate,
    WebsiteDiscoveryResult,
)
from app.services.website_discovery.providers import (
    DuckDuckGoWebsiteDiscoveryProvider,
    EmptyWebsiteDiscoveryProvider,
    WebsiteDiscoveryProvider,
)


BLOCKED_DOMAINS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
    "x.com",
    "twitter.com",
    "tiktok.com",
    "wikipedia.org",
    "tripadvisor.com",
}


class WebsiteDiscoveryService:
    """
    Discover and verify the most likely official website
    for a business.
    """

    def __init__(
        self,
        providers: Iterable[
            WebsiteDiscoveryProvider
        ] | None = None,
    ) -> None:
        self.providers = list(
    providers
    or [
        DuckDuckGoWebsiteDiscoveryProvider(),
        EmptyWebsiteDiscoveryProvider(),
    ]
)

    async def discover(
        self,
        *,
        business_name: str,
        location: str,
        limit_per_provider: int = 5,
    ) -> WebsiteDiscoveryResult:
        candidates: list[
            WebsiteCandidate
        ] = []

        errors: list[str] = []

        for provider in self.providers:
            try:
                provider_candidates = (
                    await provider.search(
                        business_name=business_name,
                        location=location,
                        limit=limit_per_provider,
                    )
                )

                candidates.extend(
                    provider_candidates
                )

            except Exception as exc:
                errors.append(
                    f"{provider.name}: {exc}"
                )

        ranked_candidates = sorted(
            self._deduplicate_candidates(
                candidates
            ),
            key=lambda candidate:
                candidate.confidence,
            reverse=True,
        )

        for candidate in ranked_candidates:
            if self._is_blocked_url(
                candidate.url
            ):
                continue

            is_verified = (
                await self._verify_candidate(
                    candidate.url
                )
            )

            candidate.verified = (
                is_verified
            )

            if is_verified:
                return WebsiteDiscoveryResult(
                    business_name=business_name,
                    location=location,
                    website=candidate.url,
                    status="found",
                    provider=candidate.provider,
                    confidence=candidate.confidence,
                    candidates=ranked_candidates,
                    errors=errors,
                )

        return WebsiteDiscoveryResult(
            business_name=business_name,
            location=location,
            website=None,
            status="not_found",
            provider=None,
            confidence=0,
            candidates=ranked_candidates,
            errors=errors,
        )

    @staticmethod
    def _deduplicate_candidates(
        candidates: list[
            WebsiteCandidate
        ],
    ) -> list[WebsiteCandidate]:
        deduplicated: dict[
            str,
            WebsiteCandidate,
        ] = {}

        for candidate in candidates:
            normalized_url = (
                WebsiteDiscoveryService
                ._normalize_url(
                    candidate.url
                )
            )

            if not normalized_url:
                continue

            existing = deduplicated.get(
                normalized_url
            )

            if (
                existing is None
                or candidate.confidence
                > existing.confidence
            ):
                candidate.url = normalized_url
                deduplicated[
                    normalized_url
                ] = candidate

        return list(
            deduplicated.values()
        )

    @staticmethod
    def _normalize_url(
        value: str,
    ) -> str:
        cleaned = str(value or "").strip()

        if not cleaned:
            return ""

        if not cleaned.startswith(
            (
                "http://",
                "https://",
            )
        ):
            cleaned = (
                f"https://{cleaned}"
            )

        return cleaned.rstrip("/")

    @staticmethod
    def _is_blocked_url(
        value: str,
    ) -> bool:
        try:
            domain = (
                urlparse(value)
                .netloc
                .lower()
                .removeprefix("www.")
            )

            return any(
                domain == blocked
                or domain.endswith(
                    f".{blocked}"
                )
                for blocked
                in BLOCKED_DOMAINS
            )

        except ValueError:
            return True

    @staticmethod
    async def _verify_candidate(
        website: str,
    ) -> bool:
        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "NestoraAI/0.9 "
                        "(website-discovery)"
                    )
                },
            ) as client:
                response = await client.get(
                    website
                )

            content_type = (
                response.headers.get(
                    "content-type",
                    "",
                )
                .lower()
            )

            return bool(
                response.status_code < 500
                and (
                    "text/html"
                    in content_type
                    or not content_type
                )
            )

        except httpx.HTTPError:
            return False