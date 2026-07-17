from app.schemas.mission import MissionRequest


def build_execution_plan(request: MissionRequest):
    """
    CEO Agent creates an execution plan.

    This function does NOT execute anything.
    It only describes the work that must be done.
    """

    plan = [
        {
            "agent": "Research Agent",
            "task_type": "business_search",
            "title": f"Find {request.business_type}",
            "description": (
                f"Search for {request.quantity} "
                f"{request.business_type} businesses "
                f"in {request.location}"
            ),
            "priority": "high",
            "sequence": 1,
        },
        {
            "agent": "CRM Agent",
            "task_type": "save_leads",
            "title": "Save Leads",
            "description": "Store discovered businesses inside CRM.",
            "priority": "high",
            "sequence": 2,
        },
        {
            "agent": "Sales Agent",
            "task_type": "lead_analysis",
            "title": "Analyze Leads",
            "description": "Score and prioritize all CRM leads.",
            "priority": "high",
            "sequence": 3,
        },
    ]

    if request.analyze_websites:
        plan.append(
            {
                "agent": "Website Agent",
                "task_type": "website_analysis",
                "title": "Analyze Websites",
                "description": "Inspect company websites.",
                "priority": "medium",
                "sequence": len(plan) + 1,
            }
        )

    if request.generate_outreach:
        plan.append(
            {
                "agent": "Outreach Agent",
                "task_type": "generate_outreach",
                "title": "Generate Outreach",
                "description": "Create personalized outreach messages.",
                "priority": "medium",
                "sequence": len(plan) + 1,
            }
        )

    plan.append(
        {
            "agent": "Proposal Agent",
            "task_type": "proposal_generation",
            "title": "Generate Proposal",
            "description": "Prepare a business proposal.",
            "priority": "low",
            "sequence": len(plan) + 1,
        }
    )

    return plan