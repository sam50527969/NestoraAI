import asyncio

from app.services.competitor_enrichment.email_discovery import (
    discover_email,
)
from app.services.competitor_enrichment.phone_discovery import (
    _discover_from_website,
)
from app.services.competitor_enrichment.website_discovery import (
    _verify_website,
)
from app.services.website_discovery.service import (
    WebsiteDiscoveryService,
)
from app.services.website_intelligence.crawler import (
    crawl_website,
)


PRIVATE_URL = (
    "http://169.254.169.254/"
    "latest/meta-data/"
)


def test_crawler_blocks_private_destination():
    result = asyncio.run(
        crawl_website(
            PRIVATE_URL
        )
    )

    assert result.status_code is None
    assert result.html == ""
    assert result.error is not None
    assert "blocked" in result.error.lower()


def test_email_discovery_blocks_private_destination():
    result = asyncio.run(
        discover_email(
            business_name="Security Test",
            website=PRIVATE_URL,
            current_email=None,
        )
    )

    assert result["email"] == "Not found"
    assert result["status"] == "missing"


def test_phone_discovery_blocks_private_destination():
    result = asyncio.run(
        _discover_from_website(
            PRIVATE_URL
        )
    )

    assert result is None


def test_competitor_website_verifier_blocks_private_destination():
    result = asyncio.run(
        _verify_website(
            PRIVATE_URL
        )
    )

    assert result is False


def test_website_discovery_verifier_blocks_private_destination():
    result = asyncio.run(
        WebsiteDiscoveryService._verify_candidate(
            PRIVATE_URL
        )
    )

    assert result is False
