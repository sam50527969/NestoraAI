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


EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)


def _has_value(value: Any) -> bool:
    cleaned = str(value or "").strip().lower()

    return (
        cleaned
        and cleaned not in INVALID_VALUES
    )


async def discover_email(
    *,
    business_name: str,
    website: Any = None,
    current_email: Any = None,
) -> dict[str, Any]:
    del business_name

    if _has_value(current_email):
        return {
            "email": str(current_email),
            "confidence": 95,
            "source": "existing_business_record",
            "status": "verified",
        }

    if _has_value(website):
        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    str(website)
                )

                match = EMAIL_PATTERN.search(
                    response.text
                )

                if match:
                    return {
                        "email": match.group(0),
                        "confidence": 80,
                        "source": "official_website",
                        "status": "discovered",
                    }

        except Exception:
            pass

    return {
        "email": "Not found",
        "confidence": 0,
        "source": None,
        "status": "missing",
    }