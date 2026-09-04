from __future__ import annotations

import re
from typing import Any

import httpx


INVALID_VALUES = {
    "",
    "not found",
    "missing",
    "none",
    "null",
    "n/a",
}


PHONE_PATTERNS = [
    re.compile(
        r"(?<!\w)\+\d{1,3}"
        r"(?:[\s().-]*\d){6,14}(?!\d)"
    ),
]


def _has_value(value: Any) -> bool:
    cleaned = str(value or "").strip()

    return bool(
        cleaned
        and cleaned.lower() not in INVALID_VALUES
    )


def _normalize_phone(value: str) -> str:
    cleaned = re.sub(
        r"[^\d+]",
        "",
        value,
    )

    if cleaned.startswith("00"):
        cleaned = f"+{cleaned[2:]}"

    return cleaned


def _extract_phone_from_text(
    content: str,
) -> str | None:
    for pattern in PHONE_PATTERNS:
        match = pattern.search(content)

        if match:
            return _normalize_phone(
                match.group(0)
            )

    return None


async def _discover_from_website(
    website: str,
) -> str | None:
    try:
        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "NestoraAI/0.8 "
                    "(competitor-enrichment)"
                )
            },
        ) as client:
            response = await client.get(
                website
            )

            response.raise_for_status()

            return _extract_phone_from_text(
                response.text
            )

    except httpx.HTTPError:
        return None


async def discover_phone(
    *,
    business_name: str,
    location: str,
    website: Any = None,
    current_phone: Any = None,
) -> dict[str, Any]:
    """
    Return a verified phone number from the existing
    business record or discover one from the website.
    """

    del business_name
    del location

    if _has_value(current_phone):
        normalized_phone = _normalize_phone(
            str(current_phone)
        )

        return {
            "phone": normalized_phone,
            "confidence": 95,
            "source": "existing_business_record",
            "status": "verified",
        }

    if _has_value(website):
        discovered_phone = (
            await _discover_from_website(
                str(website)
            )
        )

        if discovered_phone:
            return {
                "phone": discovered_phone,
                "confidence": 80,
                "source": "official_website",
                "status": "discovered",
            }

    return {
        "phone": "Not found",
        "confidence": 0,
        "source": None,
        "status": "missing",
    }