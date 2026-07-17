import uuid

from app.database.database import SessionLocal
from app.schemas.crm import LeadCreate
from app.schemas.outreach import OutreachLead, OutreachRequest
from app.services.business_search import search_businesses
from app.services.crm_service import create_lead, update_ai_analysis
from app.services.mission_activity import log_mission_activity
from app.services.mission_filters import filter_leads, has_real_value
from app.services.mission_task_planner import create_mission_task_plan
from app.services.mission_task_runtime import (
    complete_mission_task,
    fail_mission_task,
    start_mission_task,
    update_mission_task_progress,
)
from app.services.opportunity_engine import analyze_opportunity
from app.services.outreach_service import generate_outreach
from app.services.sales_ai import analyze_lead
from app.services.website_analyzer import analyze_website


MISSIONS = {}


def build_default_agents():
    return [
        {
            "name": "CEO Agent",
            "role": "Mission planning",
            "icon": "🧠",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting to plan mission",
        },
        {
            "name": "Research Agent",
            "role": "Business discovery",
            "icon": "🔍",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for mission",
        },
        {
            "name": "CRM Agent",
            "role": "Lead storage",
            "icon": "💾",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for businesses",
        },
        {
            "name": "Sales Agent",
            "role": "Lead scoring",
            "icon": "📈",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for CRM records",
        },
        {
            "name": "Website Agent",
            "role": "Website intelligence",
            "icon": "🌐",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for websites",
        },
        {
            "name": "Outreach Agent",
            "role": "Message generation",
            "icon": "📧",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for analysis",
        },
        {
            "name": "Proposal Agent",
            "role": "Proposal preparation",
            "icon": "📝",
            "status": "waiting",
            "progress": 0,
            "current_task": "Not enabled for this mission",
        },
    ]


def create_mission():
    mission_id = str(uuid.uuid4())

    MISSIONS[mission_id] = {
        "mission_id": mission_id,
        "status": "queued",
        "progress": 0,
        "current_step": "Waiting",
        "searched": 0,
        "analyzed": 0,
        "outreach_generated": 0,
        "task_count": 0,
        "agents": build_default_agents(),
        "activity": [],
    }

    return MISSIONS[mission_id]


def update_mission(mission_id, **kwargs):
    mission = MISSIONS.get(mission_id)

    if mission:
        mission.update(kwargs)


def update_agent(
    mission_id,
    agent_name,
    *,
    status=None,
    progress=None,
    current_task=None,
):
    mission = MISSIONS.get(mission_id)

    if not mission:
        return

    for agent in mission["agents"]:
        if agent["name"] != agent_name:
            continue

        if status is not None:
            agent["status"] = status

        if progress is not None:
            agent["progress"] = max(
                0,
                min(int(progress), 100),
            )

        if current_task is not None:
            agent["current_task"] = current_task

        break


def fail_running_agents(mission_id):
    mission = MISSIONS.get(mission_id)

    if not mission:
        return

    for agent in mission["agents"]:
        if agent["status"] == "running":
            agent["status"] = "failed"
            agent["current_task"] = (
                "Agent stopped because mission failed"
            )


def get_mission(mission_id):
    return MISSIONS.get(mission_id)


def complete_empty_mission(
    db,
    mission_id,
    *,
    current_step,
    raw_result_count,
    rejected_count,
):
    complete_mission_task(
        db,
        mission_id,
        "save_leads",
        output_data={
            "saved_count": 0,
            "reason": "No businesses matched the filters",
        },
    )

    complete_mission_task(
        db,
        mission_id,
        "lead_analysis",
        output_data={
            "analyzed_count": 0,
            "reason": "No leads were available",
        },
    )

    complete_mission_task(
        db,
        mission_id,
        "website_analysis",
        output_data={
            "websites_analyzed": 0,
            "skipped": True,
            "reason": "No websites were available",
        },
    )

    complete_mission_task(
        db,
        mission_id,
        "generate_outreach",
        output_data={
            "outreach_generated": 0,
            "skipped": True,
            "reason": "No leads were available",
        },
    )

    complete_mission_task(
        db,
        mission_id,
        "proposal_generation",
        output_data={
            "skipped": True,
            "reason": "Proposal generation is not enabled yet",
        },
    )

    update_agent(
        mission_id,
        "CRM Agent",
        status="completed",
        progress=100,
        current_task="No businesses matched the filters",
    )

    update_agent(
        mission_id,
        "Sales Agent",
        status="completed",
        progress=100,
        current_task="No leads to analyze",
    )

    update_agent(
        mission_id,
        "Website Agent",
        status="completed",
        progress=100,
        current_task="No websites to analyze",
    )

    update_agent(
        mission_id,
        "Outreach Agent",
        status="completed",
        progress=100,
        current_task="No outreach required",
    )

    update_agent(
        mission_id,
        "Proposal Agent",
        status="completed",
        progress=100,
        current_task="Proposal generation skipped",
    )

    log_mission_activity(
        MISSIONS[mission_id],
        "CEO Agent",
        current_step,
    )

    update_mission(
        mission_id,
        status="completed",
        progress=100,
        current_step=current_step,
        searched=0,
        analyzed=0,
        outreach_generated=0,
        raw_results=raw_result_count,
        rejected=rejected_count,
    )


async def run_real_mission(mission_id, request):
    db = SessionLocal()
    active_task_type = None

    try:
        mission_tasks = create_mission_task_plan(
            db,
            mission_id,
            request,
        )

        update_mission(
            mission_id,
            task_count=len(mission_tasks),
        )

        log_mission_activity(
            MISSIONS[mission_id],
            "CEO Agent",
            (
                f"Created execution plan with "
                f"{len(mission_tasks)} tasks."
            ),
        )

        update_mission(
            mission_id,
            status="running",
            progress=3,
            current_step="CEO Agent is planning the mission",
        )

        log_mission_activity(
            MISSIONS[mission_id],
            "CEO Agent",
            "Mission started.",
        )

        update_agent(
            mission_id,
            "CEO Agent",
            status="running",
            progress=50,
            current_task="Planning mission workflow",
        )

        update_agent(
            mission_id,
            "CEO Agent",
            status="completed",
            progress=100,
            current_task="Mission plan completed",
        )

        log_mission_activity(
            MISSIONS[mission_id],
            "CEO Agent",
            "Mission plan completed.",
        )

        # ---------------------------------------------------------
        # Research task
        # ---------------------------------------------------------

        active_task_type = "business_search"

        start_mission_task(
            db,
            mission_id,
            active_task_type,
        )

        update_mission_task_progress(
            db,
            mission_id,
            active_task_type,
            10,
        )

        update_agent(
            mission_id,
            "Research Agent",
            status="running",
            progress=10,
            current_task=(
                f"Searching for {request.business_type} "
                f"businesses in {request.location}"
            ),
        )

        update_mission(
            mission_id,
            progress=8,
            current_step="Research Agent is searching businesses",
        )

        log_mission_activity(
            MISSIONS[mission_id],
            "Research Agent",
            (
                f"Searching for {request.business_type} "
                f"businesses in {request.location}."
            ),
        )

        search_results = await search_businesses(
            business_type=request.business_type,
            location=request.location,
            limit=request.quantity,
        )

        raw_result_count = len(search_results)

        update_mission_task_progress(
            db,
            mission_id,
            active_task_type,
            80,
        )

        update_agent(
            mission_id,
            "Research Agent",
            status="running",
            progress=80,
            current_task=(
                f"Filtering {raw_result_count} search results"
            ),
        )

        leads = filter_leads(
            search_results,
            minimum_quality=request.minimum_quality,
            priority_filter=request.priority_filter,
        )

        accepted_count = len(leads)
        rejected_count = raw_result_count - accepted_count

        complete_mission_task(
            db,
            mission_id,
            active_task_type,
            output_data={
                "raw_result_count": raw_result_count,
                "accepted_count": accepted_count,
                "rejected_count": rejected_count,
                "business_type": request.business_type,
                "location": request.location,
            },
        )

        active_task_type = None

        update_agent(
            mission_id,
            "Research Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Accepted {accepted_count} businesses "
                f"and rejected {rejected_count}"
            ),
        )

        log_mission_activity(
            MISSIONS[mission_id],
            "Research Agent",
            (
                f"Accepted {accepted_count} qualified businesses "
                f"and rejected {rejected_count}."
            ),
        )

        update_mission(
            mission_id,
            progress=25,
            current_step=(
                f"Research completed with "
                f"{accepted_count} accepted businesses"
            ),
            searched=accepted_count,
        )

        if accepted_count == 0:
            complete_empty_mission(
                db,
                mission_id,
                current_step=(
                    "Mission completed with no businesses "
                    "matching the selected filters"
                ),
                raw_result_count=raw_result_count,
                rejected_count=rejected_count,
            )
            return

        analyzed_count = 0
        outreach_count = 0
        saved_count = 0
        websites_analyzed = 0

        websites_to_analyze = sum(
            1
            for lead in leads
            if has_real_value(lead.get("website"))
        )

        # ---------------------------------------------------------
        # Start CRM and Sales tasks
        # ---------------------------------------------------------

        start_mission_task(
            db,
            mission_id,
            "save_leads",
        )

        start_mission_task(
            db,
            mission_id,
            "lead_analysis",
        )

        update_agent(
            mission_id,
            "CRM Agent",
            status="running",
            progress=0,
            current_task="Preparing CRM records",
        )

        update_agent(
            mission_id,
            "Sales Agent",
            status="running",
            progress=0,
            current_task="Preparing lead analysis",
        )

        # ---------------------------------------------------------
        # Website task setup
        # ---------------------------------------------------------

        if request.analyze_websites:
            start_mission_task(
                db,
                mission_id,
                "website_analysis",
            )

            update_agent(
                mission_id,
                "Website Agent",
                status="running",
                progress=0,
                current_task="Preparing website analysis",
            )
        else:
            complete_mission_task(
                db,
                mission_id,
                "website_analysis",
                output_data={
                    "skipped": True,
                    "reason": "Website analysis was disabled",
                    "websites_analyzed": 0,
                },
            )

            update_agent(
                mission_id,
                "Website Agent",
                status="completed",
                progress=100,
                current_task="Website analysis disabled",
            )

        # ---------------------------------------------------------
        # Outreach task setup
        # ---------------------------------------------------------

        if request.generate_outreach:
            update_agent(
                mission_id,
                "Outreach Agent",
                status="waiting",
                progress=0,
                current_task="Waiting for lead analysis",
            )
        else:
            complete_mission_task(
                db,
                mission_id,
                "generate_outreach",
                output_data={
                    "skipped": True,
                    "reason": "Outreach generation was disabled",
                    "outreach_generated": 0,
                },
            )

            update_agent(
                mission_id,
                "Outreach Agent",
                status="completed",
                progress=100,
                current_task="Outreach generation disabled",
            )

        # ---------------------------------------------------------
        # Process accepted leads
        # ---------------------------------------------------------

        for index, lead in enumerate(
            leads,
            start=1,
        ):
            business_name = str(
                lead.get("businessName") or "Unnamed Business"
            ).strip()

            category = lead.get("category")
            phone = lead.get("phone")
            website = lead.get("website")
            priority = lead.get("priority") or "Medium"

            search_recommendation = lead.get(
                "aiRecommendation"
            )

            item_progress = int(
                (index / accepted_count) * 100
            )

            # -----------------------------------------------------
            # CRM task
            # -----------------------------------------------------

            active_task_type = "save_leads"

            update_mission_task_progress(
                db,
                mission_id,
                active_task_type,
                item_progress,
            )

            update_mission(
                mission_id,
                current_step=(
                    f"CRM Agent is saving {business_name}"
                ),
                progress=25 + int(
                    (index / accepted_count) * 20
                ),
            )

            update_agent(
                mission_id,
                "CRM Agent",
                status="running",
                progress=item_progress,
                current_task=f"Saving {business_name}",
            )

            crm_lead = LeadCreate(
                name=business_name,
                category=category,
                address=lead.get("location"),
                phone=(
                    phone
                    if has_real_value(phone)
                    else None
                ),
                website=(
                    website
                    if has_real_value(website)
                    else None
                ),
                source="Mission AI",
            )

            saved_lead = create_lead(
                db=db,
                lead_data=crm_lead,
            )

            saved_count += 1

            log_mission_activity(
                MISSIONS[mission_id],
                "CRM Agent",
                f"Saved {business_name}.",
            )

            # -----------------------------------------------------
            # Sales task
            # -----------------------------------------------------

            active_task_type = "lead_analysis"

            update_mission_task_progress(
                db,
                mission_id,
                active_task_type,
                item_progress,
            )

            update_mission(
                mission_id,
                current_step=(
                    f"Sales Agent is analyzing {business_name}"
                ),
                progress=45 + int(
                    (index / accepted_count) * 20
                ),
            )

            update_agent(
                mission_id,
                "Sales Agent",
                status="running",
                progress=item_progress,
                current_task=f"Scoring {business_name}",
            )

            lead_analysis_input = {
                "name": business_name,
                "category": category,
                "phone": phone,
                "website": website,
                "priority": priority,
                "notes": search_recommendation,
            }

            analysis = analyze_lead(
                lead_analysis_input
            )

            saved_lead.priority = priority

            update_ai_analysis(
                db=db,
                lead=saved_lead,
                analysis=analysis,
            )

            opportunity = analyze_opportunity(
                {
                    "website": website,
                    "phone": phone,
                    "email": lead.get("email"),
                    "priority": priority,
                    "category": category,
                    "ai_score": analysis.get("score", 0),
                }
            )

            saved_lead.opportunity_score = (
                opportunity["opportunity_score"]
            )

            saved_lead.estimated_value = (
                opportunity["estimated_value"]
            )

            saved_lead.closing_probability = (
                opportunity["closing_probability"]
            )

            saved_lead.business_potential = (
                opportunity["business_potential"]
            )

            saved_lead.opportunity_recommendation = (
                opportunity["recommended_service"]
            )

            db.commit()
            db.refresh(saved_lead)

            log_mission_activity(
                MISSIONS[mission_id],
                "Opportunity Agent",
                (
                    f"{business_name} → "
                    f"{opportunity['business_potential']} "
                    f"Opportunity "
                    f"(QAR {opportunity['estimated_value']})"
                ),
            )

            log_mission_activity(
                MISSIONS[mission_id],
                "Sales Agent",
                (
                    f"Scored {business_name} "
                    f"({analysis.get('score', 0)})."
                ),
            )

            # -----------------------------------------------------
            # Website task
            # -----------------------------------------------------

            if (
                request.analyze_websites
                and has_real_value(website)
            ):
                active_task_type = "website_analysis"

                website_progress = (
                    int(
                        (
                            websites_analyzed + 1
                        )
                        / websites_to_analyze
                        * 100
                    )
                    if websites_to_analyze
                    else 100
                )

                update_mission_task_progress(
                    db,
                    mission_id,
                    active_task_type,
                    website_progress,
                )

                update_agent(
                    mission_id,
                    "Website Agent",
                    status="running",
                    progress=website_progress,
                    current_task=(
                        f"Analyzing {business_name} website"
                    ),
                )

                try:
                    analyze_website(website)

                    log_mission_activity(
                        MISSIONS[mission_id],
                        "Website Agent",
                        (
                            f"Analyzed website for "
                            f"{business_name}."
                        ),
                    )

                except Exception as website_error:
                    print(
                        "Website analysis failed for "
                        f"{business_name}: {website_error}"
                    )

                    log_mission_activity(
                        MISSIONS[mission_id],
                        "Website Agent",
                        (
                            f"Website analysis failed for "
                            f"{business_name}."
                        ),
                    )

                websites_analyzed += 1

            analyzed_count += 1

            update_mission(
                mission_id,
                analyzed=analyzed_count,
            )

            # -----------------------------------------------------
            # Outreach task
            # -----------------------------------------------------

            if request.generate_outreach:
                active_task_type = "generate_outreach"

                if outreach_count == 0:
                    start_mission_task(
                        db,
                        mission_id,
                        active_task_type,
                    )

                update_mission_task_progress(
                    db,
                    mission_id,
                    active_task_type,
                    item_progress,
                )

                update_mission(
                    mission_id,
                    current_step=(
                        "Outreach Agent is preparing "
                        f"a message for {business_name}"
                    ),
                    progress=65 + int(
                        (index / accepted_count) * 30
                    ),
                )

                update_agent(
                    mission_id,
                    "Outreach Agent",
                    status="running",
                    progress=item_progress,
                    current_task=(
                        f"Writing outreach for "
                        f"{business_name}"
                    ),
                )

                outreach_request = OutreachRequest(
                    lead=OutreachLead(
                        name=business_name,
                        category=category,
                        phone=phone,
                        website=website,
                        priority=priority,
                        notes=analysis.get(
                            "recommendation"
                        ),
                    ),
                    offer=(
                        "99 QAR starter business package"
                    ),
                )

                generate_outreach(
                    outreach_request
                )

                outreach_count += 1

                update_mission(
                    mission_id,
                    outreach_generated=outreach_count,
                )

                log_mission_activity(
                    MISSIONS[mission_id],
                    "Outreach Agent",
                    (
                        f"Generated outreach for "
                        f"{business_name}."
                    ),
                )

        # ---------------------------------------------------------
        # Complete persistent tasks
        # ---------------------------------------------------------

        complete_mission_task(
            db,
            mission_id,
            "save_leads",
            output_data={
                "saved_count": saved_count,
            },
        )

        complete_mission_task(
            db,
            mission_id,
            "lead_analysis",
            output_data={
                "analyzed_count": analyzed_count,
            },
        )

        if request.analyze_websites:
            complete_mission_task(
                db,
                mission_id,
                "website_analysis",
                output_data={
                    "websites_analyzed": websites_analyzed,
                    "websites_available": websites_to_analyze,
                },
            )

        if request.generate_outreach:
            complete_mission_task(
                db,
                mission_id,
                "generate_outreach",
                output_data={
                    "outreach_generated": outreach_count,
                },
            )

        complete_mission_task(
            db,
            mission_id,
            "proposal_generation",
            output_data={
                "skipped": True,
                "reason": (
                    "Proposal generation is planned "
                    "for a future sprint"
                ),
            },
        )

        active_task_type = None

        # ---------------------------------------------------------
        # Complete visible agents
        # ---------------------------------------------------------

        update_agent(
            mission_id,
            "CRM Agent",
            status="completed",
            progress=100,
            current_task=f"Saved {saved_count} leads",
        )

        update_agent(
            mission_id,
            "Sales Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Analyzed {analyzed_count} leads"
            ),
        )

        update_agent(
            mission_id,
            "Website Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Analyzed {websites_analyzed} websites"
                if request.analyze_websites
                else "Website analysis disabled"
            ),
        )

        update_agent(
            mission_id,
            "Outreach Agent",
            status="completed",
            progress=100,
            current_task=(
                f"Generated {outreach_count} "
                "outreach messages"
                if request.generate_outreach
                else "Outreach generation disabled"
            ),
        )

        update_agent(
            mission_id,
            "Proposal Agent",
            status="completed",
            progress=100,
            current_task=(
                "Proposal generation skipped "
                "until the feature is implemented"
            ),
        )

        log_mission_activity(
            MISSIONS[mission_id],
            "CEO Agent",
            "Mission completed successfully.",
        )

        update_mission(
            mission_id,
            status="completed",
            progress=100,
            current_step="Mission completed",
            searched=accepted_count,
            analyzed=analyzed_count,
            outreach_generated=outreach_count,
        )

    except Exception as error:
        db.rollback()

        print(f"Real mission failed: {error}")

        if active_task_type:
            try:
                fail_mission_task(
                    db,
                    mission_id,
                    active_task_type,
                    str(error),
                )
            except Exception as task_error:
                print(
                    "Could not mark persistent task as failed: "
                    f"{task_error}"
                )

        fail_running_agents(mission_id)

        if mission_id in MISSIONS:
            log_mission_activity(
                MISSIONS[mission_id],
                "CEO Agent",
                f"Mission failed: {error}",
            )

        update_mission(
            mission_id,
            status="failed",
            progress=100,
            current_step=f"Mission failed: {error}",
        )

    finally:
        db.close()