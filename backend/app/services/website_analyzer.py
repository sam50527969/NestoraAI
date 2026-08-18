from __future__ import annotations

from urllib.parse import urlparse


def analyze_website(
    url: str,
) -> dict[str, object]:
    parsed = urlparse(url)

    score = 50
    strengths: list[str] = []
    issues: list[str] = []

    if parsed.scheme.lower() == "https":
        score += 15
        strengths.append(
            "Secure HTTPS connection"
        )
    else:
        issues.append(
            "Website is not using HTTPS"
        )

    hostname = (
        parsed.hostname or ""
    ).lower()

    if hostname.startswith("www."):
        score += 5
        strengths.append(
            "Standard domain format"
        )

    if len(url) < 40:
        score += 5
        strengths.append(
            "Clean URL structure"
        )

    issues.extend(
        [
            "Performance analysis coming soon",
            "SEO audit coming soon",
            "Accessibility audit coming soon",
        ]
    )

    return {
        "score": min(
            max(score, 0),
            100,
        ),
        "strengths": strengths,
        "issues": issues,
        "recommendation": (
            "Recommend a full website audit "
            "and optimization proposal."
        ),
    }