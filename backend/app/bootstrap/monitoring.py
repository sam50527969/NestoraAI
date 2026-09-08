from __future__ import annotations

import logging

import sentry_sdk

from app.config import (
    APP_ENV,
    APP_VERSION,
    SENTRY_DSN,
    SENTRY_TRACES_SAMPLE_RATE,
)


logger = logging.getLogger(__name__)

_initialized = False


def initialize_monitoring() -> bool:
    """
    Initialize optional production error monitoring.

    Monitoring remains disabled when SENTRY_DSN is not configured.
    Repeated calls are safe and do not initialize the SDK twice.
    """

    global _initialized

    if not SENTRY_DSN:
        logger.info(
            "Production error monitoring is disabled."
        )
        return False

    if _initialized:
        return True

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=APP_ENV,
        release=f"nestora-backend@{APP_VERSION}",
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
    )

    _initialized = True

    logger.info(
        "Production error monitoring initialized."
    )

    return True
