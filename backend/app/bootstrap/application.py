from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Any, Callable

from fastapi import FastAPI

from app.bootstrap.monitoring import initialize_monitoring


LifespanHandler = Callable[
    [FastAPI],
    AbstractAsyncContextManager[Any],
]


def create_application(
    *,
    title: str = "Nestora AI",
    version: str = "1.0.0",
    lifespan: LifespanHandler | None = None,
) -> FastAPI:
    """
    Create the Nestora FastAPI application.

    This function is the single entry point for
    constructing the application. Additional
    bootstrap steps (middleware, routes, workers,
    executives, services) will gradually move here.
    """

    initialize_monitoring()

    return FastAPI(
        title=title,
        version=version,
        lifespan=lifespan,
    )