from __future__ import annotations

import re
from typing import Protocol
from urllib.parse import (
    parse_qs,
    unquote,
    urlparse,
)

import httpx
from bs4 import BeautifulSoup

from app.services.website_discovery.models import (
    WebsiteCandidate,
)


DUCKDUCKGO_HTML_URL = (
    "https://html.duckduckgo.com/html/"
)

BLOCKED_RESULT_DOMAINS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
    "x.com",
    "twitter.com",
    "tiktok.com",
    "wikipedia.org",
    "tripadvisor.com",
    "yelp.com",
}


class WebsiteDiscoveryProvider(Protocol):
    """
    Shared interface for website-discovery providers.
    """

    name: str

    async def search(
        self,
        *,
        business_name: str,
        location: str,
        limit: int = 5,
    ) -> list[WebsiteCandidate]:
        ...


def normalize_text(value: str) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .replace("&", "and")
        .split()
    )


def normalize_url(value: str) -> str:
    cleaned = str(value or "").strip()

    if not cleaned:
        return ""

    if cleaned.startswith("//"):
        cleaned = f"https:{cleaned}"

    if not cleaned.startswith(
        (
            "http://",
            "https://",
        )
    ):
        cleaned = f"https://{cleaned}"

    return cleaned


def extract_result_url(value: str) -> str:
    """
    Convert a DuckDuckGo redirect URL into the actual
    destination URL when possible.
    """

    cleaned = str(value or "").strip()

    if not cleaned:
        return ""

    parsed = urlparse(cleaned)

    query = parse_qs(
        parsed.query
    )

    redirected_url = (
        query.get("uddg")
        or query.get("rut")
    )

    if redirected_url:
        return normalize_url(
            unquote(
                redirected_url[0]
            )
        )

    return normalize_url(cleaned)


def get_domain(value: str) -> str:
    try:
        domain = (
            urlparse(
                normalize_url(value)
            )
            .netloc
            .lower()
            .removeprefix("www.")
        )

        return domain

    except ValueError:
        return ""


def is_blocked_domain(value: str) -> bool:
    domain = get_domain(value)

    if not domain:
        return True

    return any(
        domain == blocked_domain
        or domain.endswith(
            f".{blocked_domain}"
        )
        for blocked_domain in BLOCKED_RESULT_DOMAINS
    )


def calculate_name_match(
    business_name: str,
    title: str,
    snippet: str,
    url: str,
) -> int:
    target = normalize_text(
        business_name
    )

    candidate_text = normalize_text(
        " ".join(
            [
                title,
                snippet,
                get_domain(url),
            ]
        )
    )

    if not target or not candidate_text:
        return 0

    if target in candidate_text:
        return 100

    target_tokens = set(
        target.split()
    )

    candidate_tokens = set(
        candidate_text.split()
    )

    if not target_tokens:
        return 0

    overlap = len(
        target_tokens
        & candidate_tokens
    )

    return round(
        (
            overlap
            / len(target_tokens)
        )
        * 80
    )


def calculate_location_match(
    location: str,
    title: str,
    snippet: str,
) -> int:
    normalized_location = normalize_text(
        location
    )

    if not normalized_location:
        return 0

    candidate_text = normalize_text(
        f"{title} {snippet}"
    )

    location_tokens = {
        token
        for token in normalized_location.split()
        if len(token) >= 3
    }

    if not location_tokens:
        return 0

    matched_tokens = sum(
        1
        for token in location_tokens
        if token in candidate_text
    )

    return round(
        (
            matched_tokens
            / len(location_tokens)
        )
        * 100
    )


def calculate_domain_match(
    business_name: str,
    url: str,
) -> int:
    normalized_name = re.sub(
        r"[^a-z0-9]",
        "",
        normalize_text(
            business_name
        ),
    )

    normalized_domain = re.sub(
        r"[^a-z0-9]",
        "",
        get_domain(url).split(".")[0],
    )

    if not normalized_name or not normalized_domain:
        return 0

    if normalized_name == normalized_domain:
        return 100

    if (
        normalized_name in normalized_domain
        or normalized_domain in normalized_name
    ):
        return 85

    business_tokens = [
        re.sub(
            r"[^a-z0-9]",
            "",
            token,
        )
        for token in normalize_text(
            business_name
        ).split()
    ]

    meaningful_tokens = [
        token
        for token in business_tokens
        if len(token) >= 4
    ]

    if any(
        token in normalized_domain
        for token in meaningful_tokens
    ):
        return 70

    return 0


def calculate_confidence(
    *,
    name_match: int,
    location_match: int,
    domain_match: int,
) -> int:
    return min(
        100,
        round(
            name_match * 0.55
            + domain_match * 0.30
            + location_match * 0.15
        ),
    )


class DuckDuckGoWebsiteDiscoveryProvider:
    """
    Discover likely official business websites through
    DuckDuckGo's HTML search interface.

    Results are treated only as candidates. The separate
    WebsiteDiscoveryService verifies each candidate before
    accepting it.
    """

    name = "duckduckgo_html"

    async def search(
        self,
        *,
        business_name: str,
        location: str,
        limit: int = 5,
    ) -> list[WebsiteCandidate]:
        safe_limit = max(
            1,
            min(
                int(limit),
                10,
            ),
        )

        query = " ".join(
            part
            for part in [
                f'"{business_name}"',
                location,
                "official website",
            ]
            if part
        )

        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"
                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                },
            ) as client:
                response = await client.post(
                    DUCKDUCKGO_HTML_URL,
                    data={
                        "q": query,
                    },
                )

                response.raise_for_status()

        except httpx.HTTPError as exc:
            print(
                "DuckDuckGo website discovery failed: "
                f"{business_name} | {exc}"
            )

            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        candidates: list[
            WebsiteCandidate
        ] = []

        seen_urls: set[str] = set()

        result_blocks = soup.select(
            ".result"
        )

        for result_block in result_blocks:
            link = result_block.select_one(
                ".result__a"
            )

            if link is None:
                continue

            result_url = extract_result_url(
                link.get("href", "")
            )

            if (
                not result_url
                or result_url in seen_urls
                or is_blocked_domain(
                    result_url
                )
            ):
                continue

            seen_urls.add(
                result_url
            )

            title = link.get_text(
                " ",
                strip=True,
            )

            snippet_element = (
                result_block.select_one(
                    ".result__snippet"
                )
            )

            snippet = (
                snippet_element.get_text(
                    " ",
                    strip=True,
                )
                if snippet_element
                else ""
            )

            name_match = calculate_name_match(
                business_name,
                title,
                snippet,
                result_url,
            )

            location_match = (
                calculate_location_match(
                    location,
                    title,
                    snippet,
                )
            )

            domain_match = calculate_domain_match(
                business_name,
                result_url,
            )

            confidence = calculate_confidence(
                name_match=name_match,
                location_match=location_match,
                domain_match=domain_match,
            )

            candidates.append(
                WebsiteCandidate(
                    url=result_url,
                    provider=self.name,
                    title=title or None,
                    snippet=snippet or None,
                    business_name_match=name_match,
                    location_match=location_match,
                    domain_match=domain_match,
                    confidence=confidence,
                    verified=False,
                    metadata={
                        "search_query": query,
                        "domain": get_domain(
                            result_url
                        ),
                    },
                )
            )

            if len(candidates) >= safe_limit:
                break

        return candidates


class EmptyWebsiteDiscoveryProvider:
    """
    Safe fallback provider used when no external provider
    returns candidates.
    """

    name = "empty_provider"

    async def search(
        self,
        *,
        business_name: str,
        location: str,
        limit: int = 5,
    ) -> list[WebsiteCandidate]:
        del business_name
        del location
        del limit

        return []