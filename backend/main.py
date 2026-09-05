from contextlib import (
    asynccontextmanager,
)
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.bootstrap import (
    create_application,
    register_routes,
)
from app.config import (
    APP_NAME,
    CORS_ALLOWED_ORIGINS,
)
from app.core.registry import (
    executive_registry,
    load_executives,
)
from app.core.tools import (
    tool_registry,
)
from app.database.database import (
    engine,
)
from app.database.metadata import metadata
from app.tools.loader import (
    load_tools,
)


logger = logging.getLogger(
    __name__
)


metadata.create_all(
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
            "Nestora started with "
            "executive loading errors: %s",
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
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_routes(app)


@app.get("/")
def home():
    return {
        "message": (
            "Nestora AI backend "
            "is running"
        ),
    }
