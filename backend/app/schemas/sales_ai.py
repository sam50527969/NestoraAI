from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class SalesLeadInput(BaseModel):
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


class SalesAnalysisRequest(BaseModel):
    lead: SalesLeadInput


class SalesAnalysisResponse(BaseModel):
    score: int = Field(
        ge=0,
        le=100,
    )

    strengths: list[str]
    weaknesses: list[str]
    recommendation: str
    opportunity: str