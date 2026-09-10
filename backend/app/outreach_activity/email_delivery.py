import httpx

from app.config import (
    EMAIL_FROM,
    EMAIL_PROVIDER,
    RESEND_API_KEY,
)


class EmailProvider:
    def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        body: str,
        idempotency_key: str,
    ):
        raise NotImplementedError


class DisabledEmailProvider:
    def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        body: str,
        idempotency_key: str,
    ):
        raise RuntimeError(
            "External email delivery is not configured."
        )


class ResendEmailProvider:
    API_URL = "https://api.resend.com/emails"

    def __init__(
        self,
        *,
        api_key: str,
        sender: str,
    ) -> None:
        self.api_key = api_key.strip()
        self.sender = sender.strip()

        if not self.api_key:
            raise ValueError(
                "Resend API key is required."
            )

        if not self.sender:
            raise ValueError(
                "Email sender is required."
            )

    def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        body: str,
        idempotency_key: str,
    ) -> dict[str, str]:
        response = httpx.post(
            self.API_URL,
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Idempotency-Key": (
                    idempotency_key
                ),
            },
            json={
                "from": self.sender,
                "to": [recipient],
                "subject": subject,
                "text": body,
            },
            timeout=15.0,
        )

        response.raise_for_status()

        payload = response.json()

        message_id = str(
            payload.get("id", "")
        ).strip()

        if not message_id:
            raise RuntimeError(
                "Resend did not return a message ID."
            )

        return {
            "provider": "resend",
            "message_id": message_id,
        }


def build_email_provider() -> EmailProvider:
    if EMAIL_PROVIDER == "resend":
        if not RESEND_API_KEY or not EMAIL_FROM:
            return DisabledEmailProvider()

        return ResendEmailProvider(
            api_key=RESEND_API_KEY,
            sender=EMAIL_FROM,
        )

    return DisabledEmailProvider()


email_provider: EmailProvider = build_email_provider()
