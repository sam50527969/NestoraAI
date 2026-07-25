from app.core.registry.models import ExecutiveManifest


FOLLOWUP_EXECUTIVE_MANIFEST = ExecutiveManifest(
    executive_id="followup",
    name="AI Follow-up Executive",
    description=(
        "Analyzes leads, identifies follow-up priorities, "
        "estimates lead-loss risk, and recommends the best "
        "next action and communication strategy."
    ),
    version="1.0.0",
    capabilities=(
        "lead_prioritization",
        "followup_recommendation",
        "lead_loss_risk_analysis",
        "message_generation",
        "contact_channel_recommendation",
        "contact_time_recommendation",
    ),
    workers=(),
    tools=(),
    permissions=(
        "read_leads",
        "generate_recommendations",
        "generate_messages",
    ),
    supported_missions=(
        "analyze_lead",
        "recommend_followup",
        "generate_followup_message",
    ),
    enabled=True,
    metadata={
        "department": "sales",
        "category": "customer_engagement",
        "industry_agnostic": True,
    },
)