from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.approvals import (
    models as approval_models,
)
from app.bootstrap import (
    create_application,
    register_routes,
)
from app.clinic.routes import (
    router as clinic_router,
)
from app.config import APP_NAME
from app.core.registry import (
    executive_registry,
    load_executives,
)
from app.core.tools import tool_registry
from app.database import models
from app.database.database import (
    Base,
    engine,
)
from app.follow_up_activity import (
    models as follow_up_activity_models,
)
from app.outreach_activity import (
    models as outreach_activity_models,
)
from app.tools.loader import load_tools


logger = logging.getLogger(__name__)


# Importing these model modules registers their
# SQLAlchemy tables before create_all runs.
_ = (
    models,
    approval_models,
    outreach_activity_models,
    follow_up_activity_models,
)


Base.metadata.create_all(
    bind=engine,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Initialize and shut down shared
    Nestora platform services.
    """

    executive_registry.clear()
    tool_registry.clear()

    report = load_executives(
        replace=False,
        raise_on_error=False,
    )

    load_tools()

    if report.error_count:
        logger.warning(
            "Nestora started with executive "
            "loading errors: %s",
            report.to_dict(),
        )
    else:
        logger.info(
            "Executive registry initialized "
            "successfully: %s",
            report.to_dict(),
        )

    logger.info(
        "Tool registry initialized "
        "successfully: %s",
        tool_registry.list_tools(),
    )

    app.state.executive_registry = (
        executive_registry
    )

    app.state.executive_load_report = (
        report
    )

    app.state.tool_registry = (
        tool_registry
    )

    yield

    executive_registry.clear()
    tool_registry.clear()


app = create_application(
    title=APP_NAME,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_routes(app)

app.include_router(
    clinic_router
)


@app.get("/")
def home():
    return {
        "message": (
            "Nestora AI backend is running"
        ),
    }