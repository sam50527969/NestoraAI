from app.services.activity_logger import add_activity


def log_mission_activity(
    mission,
    agent_name,
    message,
):
    """
    Add an event to a mission's activity feed.

    This wrapper is the central integration point for future database
    persistence, live updates, notifications, and audit logging.
    """
    add_activity(
        mission,
        agent_name,
        message,
    )


def log_ceo_activity(mission, message):
    log_mission_activity(mission, "CEO Agent", message)


def log_research_activity(mission, message):
    log_mission_activity(mission, "Research Agent", message)


def log_crm_activity(mission, message):
    log_mission_activity(mission, "CRM Agent", message)


def log_sales_activity(mission, message):
    log_mission_activity(mission, "Sales Agent", message)


def log_website_activity(mission, message):
    log_mission_activity(mission, "Website Agent", message)


def log_outreach_activity(mission, message):
    log_mission_activity(mission, "Outreach Agent", message)


def log_opportunity_activity(mission, message):
    log_mission_activity(mission, "Opportunity Agent", message)
