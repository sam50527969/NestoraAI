from __future__ import annotations

from typing import Any


async def discover_social_profiles(
    *,
    business_name: str,
    location: str,
    website: Any = None,
) -> dict[str, Any]:
    """
    Placeholder.

    In the next version this module will
    discover Facebook, Instagram,
    LinkedIn, TikTok and X accounts.
    """

    del business_name
    del location
    del website

    return {
        "facebook": None,
        "instagram": None,
        "linkedin": None,
        "confidence": 0,
        "source": None,
    }