from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(slots=True)
class CrawlResult:
    requested_url: str
    final_url: str | None
    status_code: int | None
    html: str
    response_time_ms: int | None
    headers: dict[str, str]
    error: str | None = None


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36 "
        "NestoraAI/0.9"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_website_url(value: str) -> str:
    cleaned = str(value or "").strip()

    if not cleaned:
        return ""

    if not cleaned.startswith(
        (
            "http://",
            "https://",
        )
    ):
        return f"https://{cleaned}"

    return cleaned


async def crawl_website(
    website: str,
    *,
    timeout_seconds: float = 15,
) -> CrawlResult:
    """
    Download one website homepage safely.

    The crawler follows redirects, records response
    timing, and returns a structured result instead
    of raising network exceptions to callers.
    """

    normalized_url = normalize_website_url(
        website
    )

    if not normalized_url:
        return CrawlResult(
            requested_url=str(website or ""),
            final_url=None,
            status_code=None,
            html="",
            response_time_ms=None,
            headers={},
            error="Website URL is empty.",
        )

    started_at = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                timeout_seconds,
                connect=min(
                    timeout_seconds,
                    8,
                ),
            ),
            follow_redirects=True,
            headers=DEFAULT_HEADERS,
        ) as client:
            response = await client.get(
                normalized_url
            )

        elapsed_ms = round(
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
            .lower()
        )

        if (
            "text/html" not in content_type
            and "application/xhtml+xml"
            not in content_type
        ):
            return CrawlResult(
                requested_url=normalized_url,
                final_url=str(response.url),
                status_code=response.status_code,
                html="",
                response_time_ms=elapsed_ms,
                headers=dict(response.headers),
                error=(
                    "The URL did not return an HTML page. "
                    f"Content type: {content_type or 'unknown'}"
                ),
            )

        return CrawlResult(
            requested_url=normalized_url,
            final_url=str(response.url),
            status_code=response.status_code,
            html=response.text,
            response_time_ms=elapsed_ms,
            headers=dict(response.headers),
            error=None,
        )

    except httpx.TimeoutException:
        return CrawlResult(
            requested_url=normalized_url,
            final_url=None,
            status_code=None,
            html="",
            response_time_ms=None,
            headers={},
            error="Website request timed out.",
        )

    except httpx.HTTPError as exc:
        return CrawlResult(
            requested_url=normalized_url,
            final_url=None,
            status_code=None,
            html="",
            response_time_ms=None,
            headers={},
            error=f"Website request failed: {exc}",
        )

    except Exception as exc:
        return CrawlResult(
            requested_url=normalized_url,
            final_url=None,
            status_code=None,
            html="",
            response_time_ms=None,
            headers={},
            error=f"Unexpected crawler error: {exc}",
        )