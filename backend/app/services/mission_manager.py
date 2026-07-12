import uuid

from app.database.database import SessionLocal
from app.schemas.crm import LeadCreate
from app.schemas.outreach import OutreachLead, OutreachRequest
from app.services.business_search import search_businesses
from app.services.crm_service import create_lead, update_ai_analysis
from app.services.outreach_service import generate_outreach
from app.services.sales_ai import analyze_lead
from app.services.website_analyzer import analyze_website


MISSIONS = {}


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
    }

    return MISSIONS[mission_id]


def update_mission(mission_id, **kwargs):
    if mission_id in MISSIONS:
        MISSIONS[mission_id].update(kwargs)


def get_mission(mission_id):
    return MISSIONS.get(mission_id)


def has_real_value(value):
    if value is None:
        return False

    cleaned_value = str(value).strip()

    return bool(
        cleaned_value
        and cleaned_value.lower() != "not found"
    )


async def run_real_mission(mission_id, request):
    db = SessionLocal()

    try:
        update_mission(
            mission_id,
            status="running",
            progress=5,
            current_step="Searching businesses",
        )

        leads = await search_businesses(
            business_type=request.business_type,
            location=request.location,
            limit=request.quantity,
        )

        searched_count = len(leads)

        update_mission(
            mission_id,
            progress=30,
            current_step="Business search completed",
            searched=searched_count,
        )

        if searched_count == 0:
            update_mission(
                mission_id,
                status="completed",
                progress=100,
                current_step="Mission completed with no results",
            )
            return

        analyzed_count = 0
        outreach_count = 0

        for index, lead in enumerate(leads, start=1):
            business_name = lead.get(
                "businessName",
                "Unknown Business",
            )
            category = lead.get("category")
            phone = lead.get("phone")
            website = lead.get("website")
            priority = lead.get("priority") or "Medium"
            search_recommendation = lead.get("aiRecommendation")

            update_mission(
                mission_id,
                current_step=f"Saving {business_name} to CRM",
                progress=30 + int((index / searched_count) * 15),
            )

            crm_lead = LeadCreate(
                name=business_name,
                category=category,
                address=lead.get("location"),
                phone=phone if has_real_value(phone) else None,
                website=website if has_real_value(website) else None,
                source="Mission AI",
            )

            saved_lead = create_lead(
                db=db,
                lead_data=crm_lead,
            )

            update_mission(
                mission_id,
                current_step=f"Analyzing {business_name}",
                progress=45 + int((index / searched_count) * 25),
            )

            lead_analysis_input = {
                "name": business_name,
                "category": category,
                "phone": phone,
                "website": website,
                "priority": priority,
                "notes": search_recommendation,
            }

            analysis = analyze_lead(lead_analysis_input)

            saved_lead.priority = priority

            update_ai_analysis(
                db=db,
                lead=saved_lead,
                analysis=analysis,
            )

            if request.analyze_websites and has_real_value(website):
                try:
                    analyze_website(website)
                except Exception as error:
                    print(
                        f"Website analysis failed for "
                        f"{business_name}: {error}"
                    )

            analyzed_count += 1

            update_mission(
                mission_id,
                analyzed=analyzed_count,
            )

            if request.generate_outreach:
                update_mission(
                    mission_id,
                    current_step=(
                        f"Generating outreach for {business_name}"
                    ),
                    progress=70 + int(
                        (index / searched_count) * 25
                    ),
                )

                outreach_request = OutreachRequest(
                    lead=OutreachLead(
                        name=business_name,
                        category=category,
                        phone=phone,
                        website=website,
                        priority=priority,
                        notes=analysis.get("recommendation"),
                    ),
                    offer="99 QAR starter business package",
                )

                generate_outreach(outreach_request)

                outreach_count += 1

                update_mission(
                    mission_id,
                    outreach_generated=outreach_count,
                )

        update_mission(
            mission_id,
            status="completed",
            progress=100,
            current_step="Mission completed",
            searched=searched_count,
            analyzed=analyzed_count,
            outreach_generated=outreach_count,
        )

    except Exception as error:
        db.rollback()

        print(f"Real mission failed: {error}")

        update_mission(
            mission_id,
            status="failed",
            progress=100,
            current_step="Mission failed",
        )

    finally:
        db.close()