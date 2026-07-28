from pydantic import BaseModel, Field


class MarketingCampaign(BaseModel):
    campaign_name: str = Field(
        description="A concise professional campaign name."
    )

    objective: str = Field(
        description="The main commercial objective."
    )

    target_audience: str = Field(
        description="The customer segment targeted by the campaign."
    )

    customer_pain_points: list[str] = Field(
        description="The main customer problems or motivations."
    )

    value_proposition: str = Field(
        description="The primary reason customers should respond."
    )

    offer: str = Field(
        description="The proposed promotional offer or incentive."
    )

    call_to_action: str = Field(
        description="The exact action the customer should take."
    )

    channels: list[str] = Field(
        description="Recommended marketing channels."
    )

    timeline: list[str] = Field(
        description="A practical campaign timeline."
    )


class MarketingMessage(BaseModel):
    channel: str = Field(
        description="The channel where the message will be used."
    )

    headline: str = Field(
        description="A compelling headline or subject line."
    )

    message: str = Field(
        description="Ready-to-use customer-facing marketing copy."
    )

    call_to_action: str = Field(
        description="The action requested from the customer."
    )


class MarketingBudget(BaseModel):
    currency: str = Field(
        description="Currency used for all budget figures."
    )

    estimated_total: float = Field(
        ge=0,
        description="Estimated total campaign budget."
    )

    allocation: list[str] = Field(
        description="Suggested budget allocation by activity."
    )


class MarketingKPI(BaseModel):
    name: str = Field(
        description="Name of the performance indicator."
    )

    target: str = Field(
        description="A realistic target for the indicator."
    )

    measurement_method: str = Field(
        description="How the indicator should be measured."
    )


class MarketingReport(BaseModel):
    executive: str = Field(
        default="Marketing",
        description="The executive responsible for the report."
    )

    task_title: str = Field(
        description="The title of the assigned task."
    )

    status: str = Field(
        default="completed",
        description="Execution status."
    )

    executive_summary: str = Field(
        description="A concise summary of the recommended strategy."
    )

    campaign: MarketingCampaign

    messages: list[MarketingMessage] = Field(
        description=(
            "Ready-to-use campaign messages for relevant channels."
        )
    )

    recommended_actions: list[str] = Field(
        description="The ordered actions the business should take."
    )

    budget: MarketingBudget

    kpis: list[MarketingKPI]

    risks: list[str] = Field(
        description="Potential campaign risks and safeguards."
    )