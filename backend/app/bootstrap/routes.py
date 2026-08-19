from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
)

from app.approvals.routes import (
    router as ceo_approvals_router,
)
from app.auth.dependencies import (
    get_current_user,
)
from app.auth.routes import (
    router as auth_router,
)
from app.clinic.routes import (
    router as clinic_router,
)
from app.collaboration.routes import (
    router as collaboration_router,
)
from app.communication.routes import (
    router as communication_router,
)
from app.follow_up_activity.routes import (
    router as follow_up_activities_router,
)
from app.memory.routes import (
    router as memory_router,
)
from app.outreach_activity.routes import (
    router as outreach_activity_router,
)
from app.pipeline_activity.routes import (
    router as pipeline_activity_router,
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


def include_protected_router(
    app: FastAPI,
    router: APIRouter,
) -> None:
    app.include_router(
        router,
        dependencies=[
            Depends(
                get_current_user,
            ),
        ],
    )


def register_routes(
    app: FastAPI,
) -> None:
    """
    Register Nestora API routes.

    Authentication endpoints remain public.
    Standard business APIs require a valid
    Bearer access token.

    Realtime routes are registered separately
    because their router contains a WebSocket,
    which uses a different authentication
    mechanism.
    """

    app.include_router(
        auth_router
    )

    protected_routers = [
        clinic_router,
        leads_router,
        search_router,
        crm_router,
        dashboard_router,
        outreach_router,
        outreach_activity_router,
        sales_ai_router,
        website_router,
        ai_agent_router,
        mission_router,
        mission_events_router,
        agent_tasks_router,
        ceo_router,
        ceo_advisor_router,
        ceo_approvals_router,
        business_router,
        objective_router,
        mission_scheduler.router,
        marketing_router,
        business_analysis_router,
        memory_router,
        communication_router,
        collaboration_router,
        follow_up_activities_router,
        pipeline_activity_router,
    ]

    for router in (
        protected_routers
    ):
        include_protected_router(
            app,
            router,
        )

    # The realtime router contains both
    # HTTP and WebSocket routes. Its HTTP
    # handlers apply authentication directly.
    app.include_router(
        realtime_router
    )