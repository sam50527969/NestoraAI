from __future__ import annotations

import re
from bs4 import BeautifulSoup


EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

PHONE_REGEX = re.compile(
    r"\+?\d[\d\s().-]{7,}\d"
)


def extract_website_data(
    html: str,
) -> dict:
    """
    Extract useful business information from
    an HTML page.

    Version 1 focuses on contact details,
    SEO metadata and social links.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    title = ""

    if soup.title:
        title = soup.title.get_text(
            strip=True,
        )

    meta_description = ""

    description_tag = soup.find(
        "meta",
        attrs={
            "name": "description",
        },
    )

    if description_tag:
        meta_description = (
            description_tag.get(
                "content",
                ""
            )
        )

    emails = sorted(
        set(
            EMAIL_REGEX.findall(
                text
            )
        )
    )

    phones = sorted(
        set(
            PHONE_REGEX.findall(
                text
            )
        )
    )

    links = [
        a.get(
            "href",
            ""
        )
        for a in soup.find_all(
            "a",
            href=True,
        )
    ]

    social = {
        "facebook": next(
            (
                link
                for link in links
                if "facebook.com"
                in link
            ),
            None,
        ),
        "instagram": next(
            (
                link
                for link in links
                if "instagram.com"
                in link
            ),
            None,
        ),
        "linkedin": next(
            (
                link
                for link in links
                if "linkedin.com"
                in link
            ),
            None,
        ),
        "youtube": next(
            (
                link
                for link in links
                if "youtube.com"
                in link
            ),
            None,
        ),
        "x": next(
            (
                link
                for link in links
                if "x.com"
                in link
                or "twitter.com"
                in link
            ),
            None,
        ),
    }

    return {
        "title": title,
        "meta_description": meta_description,
        "emails": emails,
        "phones": phones,
        "social": social,
    }