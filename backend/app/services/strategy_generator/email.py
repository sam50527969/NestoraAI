from __future__ import annotations

from app.services.strategy_generator.models import (
    StrategyEmailStep,
)


def build_email_sequence(
    *,
    business_name: str,
    industry: str,
) -> list[StrategyEmailStep]:
    """
    Build a simple lead-nurture email sequence.

    This first version is deterministic and designed
    around enquiry follow-up, trust building, and
    conversion.
    """

    safe_business_name = str(
        business_name or "Business"
    ).strip()

    safe_industry = str(
        industry or "business"
    ).strip().replace("_", " ")

    return [
        StrategyEmailStep(
            day=0,
            subject=(
                f"Thanks for contacting "
                f"{safe_business_name}"
            ),
            purpose=(
                "Acknowledge the enquiry immediately and "
                "set expectations for the next step."
            ),
            call_to_action=(
                "Reply to this email or confirm the best "
                "time for a call."
            ),
        ),

        StrategyEmailStep(
            day=1,
            subject=(
                f"How {safe_business_name} can help"
            ),
            purpose=(
                f"Explain the main {safe_industry} services "
                "and the most relevant customer benefits."
            ),
            call_to_action=(
                "Book a consultation or request more "
                "information."
            ),
        ),

        StrategyEmailStep(
            day=3,
            subject="What customers usually ask us",
            purpose=(
                "Answer common questions, reduce objections, "
                "and increase trust."
            ),
            call_to_action=(
                "Ask a question or schedule an appointment."
            ),
        ),

        StrategyEmailStep(
            day=7,
            subject=(
                f"Ready to get started with "
                f"{safe_business_name}?"
            ),
            purpose=(
                "Create a clear conversion opportunity for "
                "prospects who have not yet taken action."
            ),
            call_to_action=(
                "Book now or speak with the team."
            ),
        ),

        StrategyEmailStep(
            day=14,
            subject="A quick follow-up",
            purpose=(
                "Re-engage inactive prospects without being "
                "overly aggressive."
            ),
            call_to_action=(
                "Reply if you would still like assistance."
            ),
        ),
    ]