from unittest.mock import Mock

import httpx
import pytest

from app.outreach_activity.email_delivery import (
    ResendEmailProvider,
)


def make_response(
    status_code: int,
    payload: dict,
) -> httpx.Response:
    request = httpx.Request(
        "POST",
        "https://api.resend.com/emails",
    )
    return httpx.Response(
        status_code,
        json=payload,
        request=request,
    )


def test_resend_provider_sends_expected_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post = Mock(
        return_value=make_response(
            200,
            {"id": "resend-message-001"},
        )
    )

    monkeypatch.setattr(
        httpx,
        "post",
        post,
    )

    provider = ResendEmailProvider(
        api_key="test-api-key",
        sender="Nestora <test@example.com>",
    )

    result = provider.send_email(
        recipient="owner@example.com",
        subject="Hello from Nestora",
        body="Prepared outreach body.",
        idempotency_key="outreach-email/activity-123",
    )

    assert result == {
        "provider": "resend",
        "message_id": "resend-message-001",
    }

    post.assert_called_once()

    _, kwargs = post.call_args

    assert kwargs["headers"]["Authorization"] == (
        "Bearer test-api-key"
    )
    assert kwargs["headers"]["Idempotency-Key"] == (
        "outreach-email/activity-123"
    )

    assert kwargs["json"] == {
        "from": "Nestora <test@example.com>",
        "to": ["owner@example.com"],
        "subject": "Hello from Nestora",
        "text": "Prepared outreach body.",
    }


def test_resend_provider_rejects_missing_message_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        Mock(
            return_value=make_response(
                200,
                {},
            )
        ),
    )

    provider = ResendEmailProvider(
        api_key="test-api-key",
        sender="Nestora <test@example.com>",
    )

    with pytest.raises(
        RuntimeError,
        match="message ID",
    ):
        provider.send_email(
            recipient="owner@example.com",
            subject="Hello",
            body="Body",
            idempotency_key="outreach-email/activity-123",
        )


def test_resend_provider_rejects_api_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        Mock(
            return_value=make_response(
                422,
                {
                    "message": "Invalid sender",
                },
            )
        ),
    )

    provider = ResendEmailProvider(
        api_key="test-api-key",
        sender="Nestora <test@example.com>",
    )

    with pytest.raises(httpx.HTTPStatusError):
        provider.send_email(
            recipient="owner@example.com",
            subject="Hello",
            body="Body",
            idempotency_key="outreach-email/activity-123",
        )

def test_provider_factory_defaults_to_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.outreach_activity.email_delivery as delivery

    monkeypatch.setattr(
        delivery,
        "EMAIL_PROVIDER",
        "disabled",
    )
    monkeypatch.setattr(
        delivery,
        "RESEND_API_KEY",
        "",
    )
    monkeypatch.setattr(
        delivery,
        "EMAIL_FROM",
        "",
    )

    provider = delivery.build_email_provider()

    assert isinstance(
        provider,
        delivery.DisabledEmailProvider,
    )


def test_provider_factory_disables_incomplete_resend_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.outreach_activity.email_delivery as delivery

    monkeypatch.setattr(
        delivery,
        "EMAIL_PROVIDER",
        "resend",
    )
    monkeypatch.setattr(
        delivery,
        "RESEND_API_KEY",
        "",
    )
    monkeypatch.setattr(
        delivery,
        "EMAIL_FROM",
        "Nestora <test@example.com>",
    )

    provider = delivery.build_email_provider()

    assert isinstance(
        provider,
        delivery.DisabledEmailProvider,
    )


def test_provider_factory_builds_resend_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.outreach_activity.email_delivery as delivery

    monkeypatch.setattr(
        delivery,
        "EMAIL_PROVIDER",
        "resend",
    )
    monkeypatch.setattr(
        delivery,
        "RESEND_API_KEY",
        "test-api-key",
    )
    monkeypatch.setattr(
        delivery,
        "EMAIL_FROM",
        "Nestora <test@example.com>",
    )

    provider = delivery.build_email_provider()

    assert isinstance(
        provider,
        delivery.ResendEmailProvider,
    )
    assert provider.api_key == "test-api-key"
    assert (
        provider.sender
        == "Nestora <test@example.com>"
    )


def test_resend_provider_logs_safe_http_failure(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret_api_key = "super-secret-resend-key"
    private_recipient = "private-recipient@example.com"
    private_subject = "Private outreach subject"
    private_body = "Private outreach body"

    monkeypatch.setattr(
        httpx,
        "post",
        Mock(
            return_value=make_response(
                422,
                {
                    "message": "Invalid sender",
                    "name": "validation_error",
                },
            )
        ),
    )

    provider = ResendEmailProvider(
        api_key=secret_api_key,
        sender="Nestora <test@example.com>",
    )

    with caplog.at_level("ERROR"):
        with pytest.raises(httpx.HTTPStatusError):
            provider.send_email(
                recipient=private_recipient,
                subject=private_subject,
                body=private_body,
                idempotency_key=(
                    "outreach-email/activity-safe-log"
                ),
            )

    log_output = caplog.text

    assert "Resend email rejected" in log_output
    assert "status=422" in log_output
    assert "validation_error" in log_output
    assert "Invalid sender" not in log_output

    assert secret_api_key not in log_output
    assert private_recipient not in log_output
    assert private_subject not in log_output
    assert private_body not in log_output
    assert "Authorization" not in log_output
    assert "Bearer" not in log_output
