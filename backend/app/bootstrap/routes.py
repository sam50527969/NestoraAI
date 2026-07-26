from __future__ import annotations

from fastapi import FastAPI

from app.routes import mission_scheduler
from app.routes.agent_tasks import router as agent_tasks_router
from app.routes.ai_agent import router as ai_agent_router
from app.routes.ceo import router as ceo_router
from app.routes.ceo_advisor import router as ceo_advisor_router
from app.routes.crm import router as crm_router
from app.routes.dashboard import router as dashboard_router
from app.routes.leads import router as leads_router
from app.routes.marketing import router as marketing_router
from app.routes.mission import router as mission_router
from app.routes.objective import router as objective_router
from app.routes.outreach import router as outreach_router
from app.routes.sales_ai import router as sales_ai_router
from app.routes.search import router as search_router
from app.routes.website import router as website_router
from app.routes.business import router as business_router


def register_routes(app: FastAPI) -> None:
    """
    Register all API routes for the Nestora backend.
    """

    app.include_router(leads_router)
    app.include_router(search_router)
    app.include_router(crm_router)
    app.include_router(dashboard_router)
    app.include_router(outreach_router)
    app.include_router(sales_ai_router)
    app.include_router(website_router)
    app.include_router(ai_agent_router)
    app.include_router(mission_router)
    app.include_router(agent_tasks_router)
    app.include_router(ceo_router)
    app.include_router(ceo_advisor_router)
    app.include_router(business_router)
    app.include_router(objective_router)
    app.include_router(mission_scheduler.router)
    app.include_router(marketing_router)