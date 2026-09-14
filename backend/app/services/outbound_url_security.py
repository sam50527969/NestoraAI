from __future__ import annotations

import socket

import httpx
from ipaddress import ip_address
from urllib.parse import urljoin, urlparse


BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
}

BLOCKED_HOST_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
)


class UnsafeOutboundUrlError(ValueError):
    """Raised when an outbound URL is unsafe to request."""


def validate_outbound_url(
    value: str,
    *,
    resolve_dns: bool = True,
) -> str:
    """
    Validate an HTTP(S) URL before an outbound request.

    Hostnames are resolved before network access and every
    resolved address must be globally routable.
    """
    if not isinstance(value, str):
        raise UnsafeOutboundUrlError(
            "Outbound URL must be a string."
        )

    cleaned = value.strip()

    if not cleaned:
        raise UnsafeOutboundUrlError(
            "Outbound URL must not be empty."
        )

    try:
        parsed = urlparse(cleaned)
    except ValueError as exc:
        raise UnsafeOutboundUrlError(
            "Outbound URL is invalid."
        ) from exc

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        raise UnsafeOutboundUrlError(
            "Outbound URL must use HTTP or HTTPS."
        )

    if not parsed.hostname:
        raise UnsafeOutboundUrlError(
            "Outbound URL must include a hostname."
        )

    if (
        parsed.username is not None
        or parsed.password is not None
    ):
        raise UnsafeOutboundUrlError(
            "Outbound URL must not contain credentials."
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
        raise UnsafeOutboundUrlError(
            "Private or internal outbound URLs "
            "are not allowed."
        )

    try:
        literal_address = ip_address(
            hostname
        )
    except ValueError:
        literal_address = None

    if literal_address is not None:
        if not literal_address.is_global:
            raise UnsafeOutboundUrlError(
                "Private or internal outbound URLs "
                "are not allowed."
            )

        return cleaned

    if not resolve_dns:
        return cleaned

    try:
        resolved = socket.getaddrinfo(
            hostname,
            parsed.port or (
                443
                if parsed.scheme.lower() == "https"
                else 80
            ),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise UnsafeOutboundUrlError(
            "Outbound hostname could not be resolved."
        ) from exc

    addresses = {
        item[4][0]
        for item in resolved
        if item[4]
    }

    if not addresses:
        raise UnsafeOutboundUrlError(
            "Outbound hostname did not resolve "
            "to an address."
        )

    for resolved_address in addresses:
        try:
            address = ip_address(
                resolved_address
            )
        except ValueError as exc:
            raise UnsafeOutboundUrlError(
                "Outbound hostname resolved "
                "to an invalid address."
            ) from exc

        if not address.is_global:
            raise UnsafeOutboundUrlError(
                "Outbound hostname resolved "
                "to a private or internal address."
            )

    return cleaned



MAX_SAFE_REDIRECTS = 5

REDIRECT_STATUS_CODES = {
    301,
    302,
    303,
    307,
    308,
}


async def safe_async_get(
    client: httpx.AsyncClient,
    url: str,
    *,
    max_redirects: int = MAX_SAFE_REDIRECTS,
) -> httpx.Response:
    """
    GET an external website while validating the initial
    destination and every redirect destination.
    """
    current_url = validate_outbound_url(
        url
    )

    for redirect_count in range(
        max_redirects + 1
    ):
        response = await client.get(
            current_url,
            follow_redirects=False,
        )

        if (
            response.status_code
            not in REDIRECT_STATUS_CODES
        ):
            return response

        location = response.headers.get(
            "location"
        )

        if not location:
            return response

        if redirect_count >= max_redirects:
            raise UnsafeOutboundUrlError(
                "Outbound request exceeded "
                "the redirect limit."
            )

        next_url = urljoin(
            current_url,
            location,
        )

        current_url = validate_outbound_url(
            next_url
        )

    raise UnsafeOutboundUrlError(
        "Outbound request exceeded "
        "the redirect limit."
    )
