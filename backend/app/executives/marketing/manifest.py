from app.core.registry import ExecutiveManifest


MARKETING_EXECUTIVE = ExecutiveManifest(
    executive_id="marketing",

    name="Marketing Director",

    description=(
        "Responsible for marketing strategy, "
        "campaign planning, branding, digital "
        "marketing, customer acquisition, and "
        "market intelligence."
    ),

    version="1.0.0",

    capabilities=(
        "marketing",
        "campaign_planning",
        "branding",
        "seo",
        "social_media",
        "content_creation",
        "competitor_analysis",
        "market_research",
        "advertising",
        "lead_generation",
        "budget_planning",
    ),

    workers=(
        "content_writer",
        "seo_specialist",
        "social_media_manager",
        "ads_manager",
        "graphic_designer",
        "analytics_specialist",
    ),

    tools=(
        "website_analysis",
        "campaign_planner",
        "budget_optimizer",
        "marketing_predictor",
    ),

    permissions=(
        "create_campaign",
        "approve_content",
        "allocate_budget",
        "view_crm",
    ),

    supported_missions=(
        "increase_sales",
        "increase_brand_awareness",
        "customer_acquisition",
        "market_expansion",
    ),

    metadata={
        "department": "Marketing",
        "priority": 100,
    },
)