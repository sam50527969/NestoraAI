from __future__ import annotations

import asyncio
import logging
from threading import Lock
from typing import Any

from app.realtime.connection_manager import connection_manager
from app.realtime.events import build_event


logger = logging.getLogger(__name__)


class MissionEventPublisher:
    """
    Publishes persisted mission events to connected WebSocket clients.

    Mission execution currently runs through synchronous services and
    repositories. This publisher safely forwards events to FastAPI's
    asynchronous event loop, including when called from a worker thread.
    """

    def __init__(self) -> None:
        self._event_loop: asyncio.AbstractEventLoop | None = None
        self._lock = Lock()

    def register_current_loop(self) -> None:
        """
        Register the currently running FastAPI event loop.

        This should be called from an async route or WebSocket handler.
        """

        try:
            event_loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        with self._lock:
            self._event_loop = event_loop

    def publish(
        self,
        event_data: dict[str, Any],
        business_uid: str,
    ) -> None:
        """
        Publish a mission event from synchronous or asynchronous code.

        If no FastAPI event loop has been registered yet, the event remains
        safely persisted in the database but is not broadcast live.
        """

        payload = build_event(
            "mission.event",
            event_data,
        )

        with self._lock:
            event_loop = self._event_loop

        if (
            event_loop is None
            or event_loop.is_closed()
            or not event_loop.is_running()
        ):
            logger.debug(
                "Mission event persisted but realtime loop is unavailable."
            )
            return

        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if current_loop is event_loop:
            task = event_loop.create_task(
                connection_manager.broadcast(
                    payload,
                    business_uid,
                )
            )
            task.add_done_callback(
                self._handle_task_result
            )
            return

        future = asyncio.run_coroutine_threadsafe(
            connection_manager.broadcast(
                payload,
                business_uid,
            ),
            event_loop,
        )

        future.add_done_callback(
            self._handle_future_result
        )

    @staticmethod
    def _handle_task_result(
        task: asyncio.Task,
    ) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception(
                "Realtime mission-event broadcast failed."
            )

    @staticmethod
    def _handle_future_result(
        future: Any,
    ) -> None:
        try:
            future.result()
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception(
                "Thread-safe mission-event broadcast failed."
            )


mission_event_publisher = MissionEventPublisher()
