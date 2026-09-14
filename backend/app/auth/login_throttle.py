"""Small in-process guard against repeated login failures."""

from __future__ import annotations

from collections import OrderedDict, deque
from threading import Lock
from time import monotonic
from typing import Callable


MAX_LOGIN_FAILURES = 5
LOGIN_FAILURE_WINDOW_SECONDS = 15 * 60
MAX_TRACKED_LOGIN_IDENTITIES = 5000


class LoginFailureThrottle:
    """Track recent failed logins by normalized identity."""

    def __init__(
        self,
        *,
        max_failures: int = MAX_LOGIN_FAILURES,
        window_seconds: float = LOGIN_FAILURE_WINDOW_SECONDS,
        max_identities: int = MAX_TRACKED_LOGIN_IDENTITIES,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self.max_identities = max_identities
        self._clock = clock
        self._failures: OrderedDict[
            str,
            deque[float],
        ] = OrderedDict()
        self._lock = Lock()

    def _prune(
        self,
        failures: deque[float],
        now: float,
    ) -> None:
        cutoff = now - self.window_seconds

        while failures and failures[0] <= cutoff:
            failures.popleft()

    def is_blocked(
        self,
        identity: str,
    ) -> bool:
        now = self._clock()

        with self._lock:
            failures = self._failures.get(identity)

            if failures is None:
                return False

            self._prune(failures, now)

            if not failures:
                self._failures.pop(identity, None)
                return False

            self._failures.move_to_end(identity)

            return len(failures) >= self.max_failures

    def record_failure(
        self,
        identity: str,
    ) -> None:
        now = self._clock()

        with self._lock:
            failures = self._failures.get(identity)

            if failures is None:
                failures = deque()
                self._failures[identity] = failures
            else:
                self._prune(failures, now)

            failures.append(now)
            self._failures.move_to_end(identity)

            while (
                len(self._failures)
                > self.max_identities
            ):
                self._failures.popitem(last=False)

    def reset(
        self,
        identity: str,
    ) -> None:
        with self._lock:
            self._failures.pop(identity, None)

    def clear(self) -> None:
        """Clear state; primarily useful for isolated tests."""
        with self._lock:
            self._failures.clear()


login_failure_throttle = LoginFailureThrottle()
