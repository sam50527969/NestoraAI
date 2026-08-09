from __future__ import annotations

from typing import Any

from app.services.website_intelligence.crawler import (
    crawl_website,
)
from app.services.website_intelligence.extractor import (
    extract_website_data,
)
from app.services.website_intelligence.models import (
    WebsiteContact,
    WebsiteContentSignals,
    WebsiteIntelligenceProfile,
    WebsitePages,
    WebsiteSeoSignals,
    WebsiteSocialProfiles,
    WebsiteTechnologySignals,
)


class WebsiteIntelligenceService:
    """
    Coordinate website crawling and intelligence extraction.
    """

    async def analyze(
        self,
        *,
        website: str,
        business_name: str | None = None,
    ) -> WebsiteIntelligenceProfile:
        crawl_result = await crawl_website(
            website
        )

        if crawl_result.error:
            return WebsiteIntelligenceProfile(
                website=website,
                status="failed",
                final_url=crawl_result.final_url,
                status_code=crawl_result.status_code,
                response_time_ms=(
                    crawl_result.response_time_ms
                ),
                is_https=website.lower().startswith(
                    "https://"
                ),
                confidence=0,
                errors=[crawl_result.error],
            )

        extracted = extract_website_data(
            crawl_result.html
        )

        final_url = (
            crawl_result.final_url
            or website
        )

        social = extracted.get("social") or {}

        emails = extracted.get("emails") or []
        phones = extracted.get("phones") or []

        profile = WebsiteIntelligenceProfile(
            website=website,
            status="completed",
            final_url=final_url,
            status_code=crawl_result.status_code,
            response_time_ms=(
                crawl_result.response_time_ms
            ),
            is_https=final_url.lower().startswith(
                "https://"
            ),
            confidence=self._calculate_confidence(
                extracted
            ),
            contact=WebsiteContact(
                phones=phones,
                emails=emails,
                whatsapp_links=[],
            ),
            social_profiles=WebsiteSocialProfiles(
                facebook=social.get("facebook"),
                instagram=social.get("instagram"),
                linkedin=social.get("linkedin"),
                x=social.get("x"),
                youtube=social.get("youtube"),
            ),
            pages=WebsitePages(
                homepage=final_url,
            ),
            seo=WebsiteSeoSignals(
                title=extracted.get("title"),
                meta_description=extracted.get(
                    "meta_description"
                ),
            ),
            technologies=WebsiteTechnologySignals(),
            content=WebsiteContentSignals(
                business_name=business_name,
                summary=extracted.get(
                    "meta_description"
                ),
            ),
            raw_data={
                "headers": crawl_result.headers,
                "extracted": extracted,
            },
        )

        return profile

    @staticmethod
    def _calculate_confidence(
        extracted: dict[str, Any],
    ) -> int:
        score = 20

        if extracted.get("title"):
            score += 15

        if extracted.get("meta_description"):
            score += 15

        if extracted.get("emails"):
            score += 15

        if extracted.get("phones"):
            score += 15

        social = extracted.get("social") or {}

        if any(social.values()):
            score += 20

        return min(score, 100)