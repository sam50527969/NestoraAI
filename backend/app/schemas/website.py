from __future__ import annotations

from ipaddress import ip_address
import re
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    field_validator,
)


BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
}

BLOCKED_HOST_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
)

EXPLICIT_SCHEME_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9+.-]*://"
)


def normalize_and_validate_url(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise ValueError(
            "Website URL must be a string."
        )

    cleaned = value.strip()

    if not cleaned:
        raise ValueError(
            "Website URL must not be empty."
        )

    has_explicit_scheme = bool(
        EXPLICIT_SCHEME_PATTERN.match(
            cleaned
        )
    )

    if has_explicit_scheme:
        parsed_scheme = (
            urlparse(cleaned)
            .scheme
            .lower()
        )

        if parsed_scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "Website URL must use HTTP or HTTPS."
            )
    else:
        cleaned = f"https://{cleaned}"

    parsed = urlparse(cleaned)

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Website URL must use HTTP or HTTPS."
        )

    if not parsed.hostname:
        raise ValueError(
            "Website URL must include a valid hostname."
        )

    if (
        parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            "Website URL must not contain credentials."
        )

    hostname = (
        parsed.hostname
        .strip()
        .lower()
        .rstrip(".")
    )

    if (
        hostname in BLOCKED_HOSTNAMES
        or hostname.endswith(
            BLOCKED_HOST_SUFFIXES
        )
    ):
        raise ValueError(
            "Private or internal website URLs are not allowed."
        )

    try:
        address = ip_address(
            hostname
        )
    except ValueError:
        address = None

    if (
        address is not None
        and not address.is_global
    ):
        raise ValueError(
            "Private or internal website URLs are not allowed."
        )

    return cleaned


class WebsiteRequest(BaseModel):
    url: str

    @field_validator(
        "url",
        mode="before",
    )
    @classmethod
    def validate_url(
        cls,
        value: object,
    ) -> str:
        return normalize_and_validate_url(
            value
        )


class WebsiteResponse(BaseModel):
    score: int
    strengths: list[str]
    issues: list[str]
    recommendation: str