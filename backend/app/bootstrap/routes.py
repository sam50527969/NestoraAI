from __future__ import annotations

from fastapi import FastAPI

from app.approvals.routes import (
    router as ceo_approvals_router,
)
from app.collaboration.routes import (
    router as collaboration_router,
)
from app.communication.routes import (
    router as communication_router,
)
from app.memory.routes import (
    router as memory_router,
)
from app.outreach_activity.routes import (
    router as outreach_activity_router,
)
from app.realtime.router import (
    router as realtime_router,
)
from app.routes import mission_scheduler
from app.routes.agent_tasks import (
    router as agent_tasks_router,
)
from app.routes.ai_agent import (
    router as ai_agent_router,
)
from app.routes.business import (
    router as business_router,
)
from app.routes.business_analysis import (
    router as business_analysis_router,
)
from app.routes.ceo import (
    router as ceo_router,
)
from app.routes.ceo_advisor import (
    router as ceo_advisor_router,
)
from app.routes.crm import (
    router as crm_router,
)
from app.routes.dashboard import (
    router as dashboard_router,
)
from app.routes.leads import (
    router as leads_router,
)
from app.routes.marketing import (
    router as marketing_router,
)
from app.routes.mission import (
    router as mission_router,
)
from app.routes.mission_events import (
    router as mission_events_router,
)
from app.routes.objective import (
    router as objective_router,
)
from app.routes.outreach import (
    router as outreach_router,
)
from app.routes.sales_ai import (
    router as sales_ai_router,
)
from app.routes.search import (
    router as search_router,
)
from app.routes.website import (
    router as website_router,
)
from app.follow_up_activity.routes import (
    router as follow_up_activities_router,
)


def register_routes(
    app: FastAPI,
) -> None:
    """
    Register all API routes for the Nestora
    backend.
    """

    app.include_router(leads_router)
    app.include_router(search_router)
    app.include_router(crm_router)
    app.include_router(dashboard_router)
    app.include_router(outreach_router)
    app.include_router(
        outreach_activity_router
    )
    app.include_router(sales_ai_router)
    app.include_router(website_router)
    app.include_router(ai_agent_router)
    app.include_router(mission_router)
    app.include_router(
        mission_events_router
    )
    app.include_router(
        agent_tasks_router
    )
    app.include_router(ceo_router)
    app.include_router(
        ceo_advisor_router
    )
    app.include_router(
        ceo_approvals_router
    )
    app.include_router(business_router)
    app.include_router(objective_router)
    app.include_router(
        mission_scheduler.router
    )
    app.include_router(marketing_router)
    app.include_router(
        business_analysis_router
    )
    app.include_router(realtime_router)
    app.include_router(memory_router)
    app.include_router(
        communication_router
    )
    app.include_router(
        collaboration_router
    )
    app.include_router(
    follow_up_activities_router
)