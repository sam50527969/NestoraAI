import asyncio
import socket

import pytest

from app.services.outbound_url_security import (
    UnsafeOutboundUrlError,
    validate_outbound_url,
)


def _dns_result(address: str):
    family = (
        socket.AF_INET6
        if ":" in address
        else socket.AF_INET
    )

    if family == socket.AF_INET6:
        sockaddr = (
            address,
            443,
            0,
            0,
        )
    else:
        sockaddr = (
            address,
            443,
        )

    return [
        (
            family,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            sockaddr,
        )
    ]


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "http://localhost:8000",
        "http://service.local",
        "http://service.internal",
        "http://127.0.0.1",
        "http://10.0.0.10",
        "http://172.16.0.10",
        "http://192.168.1.10",
        "http://169.254.169.254",
        "http://[::1]",
        "http://user:password@example.com",
        "ftp://example.com",
    ],
)
def test_rejects_direct_unsafe_urls(url):
    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        validate_outbound_url(
            url,
            resolve_dns=False,
        )


def test_accepts_global_literal_ip():
    result = validate_outbound_url(
        "https://8.8.8.8",
        resolve_dns=False,
    )

    assert result == "https://8.8.8.8"


def test_accepts_public_dns_resolution(
    monkeypatch,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs:
            _dns_result("93.184.216.34"),
    )

    result = validate_outbound_url(
        "https://example.com"
    )

    assert result == "https://example.com"


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.5",
        "172.16.0.5",
        "192.168.1.5",
        "169.254.169.254",
        "::1",
        "fc00::1",
        "fe80::1",
    ],
)
def test_rejects_private_dns_resolution(
    monkeypatch,
    address,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs:
            _dns_result(address),
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        validate_outbound_url(
            "https://example.com"
        )


def test_rejects_mixed_public_and_private_dns(
    monkeypatch,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: (
            _dns_result("93.184.216.34")
            + _dns_result("127.0.0.1")
        ),
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        validate_outbound_url(
            "https://example.com"
        )


def test_rejects_unresolvable_hostname(
    monkeypatch,
):
    def fail_resolution(
        *args,
        **kwargs,
    ):
        raise socket.gaierror(
            "resolution failed"
        )

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        fail_resolution,
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        validate_outbound_url(
            "https://example.invalid"
        )


def test_rejects_credentials_before_dns(
    monkeypatch,
):
    def unexpected_resolution(
        *args,
        **kwargs,
    ):
        raise AssertionError(
            "DNS should not be called."
        )

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        unexpected_resolution,
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        validate_outbound_url(
            "https://user:secret@example.com"
        )


class FakeResponse:
    def __init__(
        self,
        *,
        status_code,
        url,
        location=None,
    ):
        self.status_code = status_code
        self.url = url
        self.headers = {}

        if location is not None:
            self.headers["location"] = location


class FakeAsyncClient:
    def __init__(
        self,
        responses,
    ):
        self.responses = list(responses)
        self.requested_urls = []

    async def get(
        self,
        url,
        *,
        follow_redirects=False,
    ):
        assert follow_redirects is False

        self.requested_urls.append(url)

        if not self.responses:
            raise AssertionError(
                "Unexpected outbound request."
            )

        return self.responses.pop(0)


def test_safe_get_accepts_public_destination(
    monkeypatch,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs:
            _dns_result("93.184.216.34"),
    )

    client = FakeAsyncClient(
        [
            FakeResponse(
                status_code=200,
                url="https://example.com",
            ),
        ]
    )

    from app.services.outbound_url_security import (
        safe_async_get,
    )

    response = asyncio.run(safe_async_get(
        client,
        "https://example.com",
    ))

    assert response.status_code == 200
    assert client.requested_urls == [
        "https://example.com"
    ]


def test_safe_get_follows_public_redirect(
    monkeypatch,
):
    def resolve(
        hostname,
        *args,
        **kwargs,
    ):
        assert hostname in {
            "example.com",
            "www.example.com",
        }

        return _dns_result(
            "93.184.216.34"
        )

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        resolve,
    )

    client = FakeAsyncClient(
        [
            FakeResponse(
                status_code=301,
                url="https://example.com",
                location=(
                    "https://www.example.com/home"
                ),
            ),
            FakeResponse(
                status_code=200,
                url=(
                    "https://www.example.com/home"
                ),
            ),
        ]
    )

    from app.services.outbound_url_security import (
        safe_async_get,
    )

    response = asyncio.run(safe_async_get(
        client,
        "https://example.com",
    ))

    assert response.status_code == 200

    assert client.requested_urls == [
        "https://example.com",
        "https://www.example.com/home",
    ]


def test_safe_get_supports_relative_redirect(
    monkeypatch,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs:
            _dns_result("93.184.216.34"),
    )

    client = FakeAsyncClient(
        [
            FakeResponse(
                status_code=302,
                url="https://example.com",
                location="/about",
            ),
            FakeResponse(
                status_code=200,
                url="https://example.com/about",
            ),
        ]
    )

    from app.services.outbound_url_security import (
        safe_async_get,
    )

    asyncio.run(safe_async_get(
        client,
        "https://example.com",
    ))

    assert client.requested_urls == [
        "https://example.com",
        "https://example.com/about",
    ]


def test_safe_get_blocks_redirect_to_private_ip(
    monkeypatch,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs:
            _dns_result("93.184.216.34"),
    )

    client = FakeAsyncClient(
        [
            FakeResponse(
                status_code=302,
                url="https://example.com",
                location=(
                    "http://169.254.169.254/"
                    "latest/meta-data/"
                ),
            ),
        ]
    )

    from app.services.outbound_url_security import (
        safe_async_get,
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        asyncio.run(safe_async_get(
            client,
            "https://example.com",
        ))

    assert client.requested_urls == [
        "https://example.com"
    ]


def test_safe_get_blocks_redirect_dns_to_private(
    monkeypatch,
):
    def resolve(
        hostname,
        *args,
        **kwargs,
    ):
        if hostname == "example.com":
            return _dns_result(
                "93.184.216.34"
            )

        if hostname == "internal.example":
            return _dns_result(
                "127.0.0.1"
            )

        raise AssertionError(
            f"Unexpected hostname: {hostname}"
        )

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        resolve,
    )

    client = FakeAsyncClient(
        [
            FakeResponse(
                status_code=302,
                url="https://example.com",
                location=(
                    "https://internal.example/admin"
                ),
            ),
        ]
    )

    from app.services.outbound_url_security import (
        safe_async_get,
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        asyncio.run(safe_async_get(
            client,
            "https://example.com",
        ))

    assert client.requested_urls == [
        "https://example.com"
    ]


def test_safe_get_blocks_redirect_credentials(
    monkeypatch,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs:
            _dns_result("93.184.216.34"),
    )

    client = FakeAsyncClient(
        [
            FakeResponse(
                status_code=302,
                url="https://example.com",
                location=(
                    "https://user:secret@"
                    "example.com/private"
                ),
            ),
        ]
    )

    from app.services.outbound_url_security import (
        safe_async_get,
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        asyncio.run(safe_async_get(
            client,
            "https://example.com",
        ))

    assert client.requested_urls == [
        "https://example.com"
    ]


def test_safe_get_enforces_redirect_limit(
    monkeypatch,
):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs:
            _dns_result("93.184.216.34"),
    )

    client = FakeAsyncClient(
        [
            FakeResponse(
                status_code=302,
                url="https://example.com",
                location="/one",
            ),
            FakeResponse(
                status_code=302,
                url="https://example.com/one",
                location="/two",
            ),
        ]
    )

    from app.services.outbound_url_security import (
        safe_async_get,
    )

    with pytest.raises(
        UnsafeOutboundUrlError
    ):
        asyncio.run(safe_async_get(
            client,
            "https://example.com",
            max_redirects=1,
        ))

    assert client.requested_urls == [
        "https://example.com",
        "https://example.com/one",
    ]
