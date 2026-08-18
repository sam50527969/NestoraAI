from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


DEFAULT_OUTREACH_OFFER = (
    "starter business package"
)


class OutreachLead(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=240,
    )

    category: str | None = Field(
        default=None,
        max_length=160,
    )

    phone: str | None = Field(
        default=None,
        max_length=80,
    )

    website: str | None = Field(
        default=None,
        max_length=500,
    )

    priority: str | None = Field(
        default=None,
        max_length=40,
    )

    notes: str | None = Field(
        default=None,
        max_length=4000,
    )

    @field_validator("name")
    @classmethod
    def validate_name(
        cls,
        value: str,
    ) -> str:
        normalized_value = " ".join(
            value.strip().split()
        )

        if not normalized_value:
            raise ValueError(
                "Lead name must not be empty."
            )

        return normalized_value


class OutreachRequest(BaseModel):
    lead: OutreachLead

    offer: str | None = Field(
        default=DEFAULT_OUTREACH_OFFER,
        max_length=240,
    )

    @field_validator("offer")
    @classmethod
    def normalize_offer(
        cls,
        value: str | None,
    ) -> str:
        if value is None:
            return DEFAULT_OUTREACH_OFFER

        normalized_value = " ".join(
            value.strip().split()
        )

        return (
            normalized_value
            or DEFAULT_OUTREACH_OFFER
        )


class OutreachResponse(BaseModel):
    email_subject: str
    email_body: str
    whatsapp_message: str
    cold_call_script: str
    proposal_summary: str