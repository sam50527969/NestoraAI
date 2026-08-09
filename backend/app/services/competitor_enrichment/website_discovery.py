from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from app.services.website_discovery import (
    WebsiteDiscoveryService,
)


INVALID_VALUES = {
    "",
    "not found",
    "missing",
    "website missing",
    "none",
    "null",
    "undefined",
    "n/a",
}


def _has_value(value: Any) -> bool:
    cleaned = str(value or "").strip().lower()

    return bool(
        cleaned
        and cleaned not in INVALID_VALUES
    )


def _normalize_url(value: str) -> str:
    cleaned = str(value or "").strip()

    if not cleaned:
        return ""

    if not cleaned.startswith(
        (
            "http://",
            "https://",
        )
    ):
        cleaned = f"https://{cleaned}"

    return cleaned.rstrip("/")


def _is_valid_business_url(
    value: str,
) -> bool:
    try:
        parsed = urlparse(
            _normalize_url(value)
        )

        return bool(
            parsed.scheme
            and parsed.netloc
        )

    except ValueError:
        return False


async def _verify_website(
    website: str,
) -> bool:
    normalized = _normalize_url(
        website
    )

    if not _is_valid_business_url(
        normalized
    ):
        return False

    try:
        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "NestoraAI/0.9 "
                    "(competitor-enrichment)"
                )
            },
        ) as client:
            response = await client.get(
                normalized
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
                "text/html" in content_type
                or not content_type
            )
        )

    except httpx.HTTPError:
        return False


async def discover_website(
    *,
    business_name: str,
    location: str,
    current_website: Any = None,
) -> dict[str, Any]:
    """
    Verify an existing website first.

    If no usable website exists, search for the most
    likely official website using Nestora's website
    discovery service.
    """

    if _has_value(
        current_website
    ):
        normalized_website = _normalize_url(
            str(current_website)
        )

        is_verified = await _verify_website(
            normalized_website
        )

        if is_verified:
            return {
                "website": normalized_website,
                "confidence": 95,
                "source": "existing_business_record",
                "status": "verified",
                "candidates": [],
                "errors": [],
            }

    discovery_service = WebsiteDiscoveryService()

    discovery_result = (
        await discovery_service.discover(
            business_name=business_name,
            location=location,
            limit_per_provider=5,
        )
    )

    if (
        discovery_result.status == "found"
        and _has_value(
            discovery_result.website
        )
    ):
        return {
            "website": _normalize_url(
                str(
                    discovery_result.website
                )
            ),
            "confidence": (
                discovery_result.confidence
            ),
            "source": (
                discovery_result.provider
                or "website_discovery"
            ),
            "status": "discovered",
            "candidates": [
                candidate.to_dict()
                for candidate
                in discovery_result.candidates
            ],
            "errors": list(
                discovery_result.errors
            ),
        }

    return {
        "website": "Not found",
        "confidence": 0,
        "source": None,
        "status": "not_found",
        "candidates": [
            candidate.to_dict()
            for candidate
            in discovery_result.candidates
        ],
        "errors": list(
            discovery_result.errors
        ),
    }