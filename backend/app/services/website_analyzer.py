from urllib.parse import urlparse


def analyze_website(url: str):
    parsed = urlparse(url)

    score = 50

    strengths = []
    issues = []

    if parsed.scheme == "https":
        score += 15
        strengths.append("Secure HTTPS connection")
    else:
        issues.append("Website is not using HTTPS")

    if parsed.netloc.startswith("www."):
        score += 5
        strengths.append("Standard domain format")

    if len(url) < 40:
        score += 5
        strengths.append("Clean URL structure")

    issues.extend(
        [
            "Performance analysis coming soon",
            "SEO audit coming soon",
            "Accessibility audit coming soon",
        ]
    )

    return {
        "score": min(score, 100),
        "strengths": strengths,
        "issues": issues,
        "recommendation": (
            "Recommend a full website audit and optimization proposal."
        ),
    }