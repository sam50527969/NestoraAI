from typing import Protocol


class EmailProvider(Protocol):
    def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        body: str,
    ):
        ...


class DisabledEmailProvider:
    def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        body: str,
    ):
        raise RuntimeError(
            "External email delivery is not configured."
        )


email_provider: EmailProvider = (
    DisabledEmailProvider()
)
