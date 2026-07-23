from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.executives.context import (
    ExecutiveContext,
)
from app.core.executives.result import (
    ExecutiveResult,
)


class ExecutiveBase(ABC):
    """
    Base class for every Nestora Executive.

    Every executive follows exactly the same lifecycle.
    """

    def __init__(self) -> None:
        self.initialized = True

    async def run(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveResult:
        """
        Complete executive workflow.
        """

        await self.validate(context)

        await self.analyze(context)

        await self.plan(context)

        result = await self.execute(
            context,
        )

        await self.learn(
            context,
            result,
        )

        await self.report(
            context,
            result,
        )

        return result

    async def validate(
        self,
        context: ExecutiveContext,
    ) -> None:
        """
        Validate execution context.
        """

        if not context.mission.strip():
            raise ValueError(
                "Mission cannot be empty."
            )

    @abstractmethod
    async def analyze(
        self,
        context: ExecutiveContext,
    ) -> None:
        ...

    @abstractmethod
    async def plan(
        self,
        context: ExecutiveContext,
    ) -> None:
        ...

    @abstractmethod
    async def execute(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveResult:
        ...

    async def learn(
        self,
        context: ExecutiveContext,
        result: ExecutiveResult,
    ) -> None:
        """
        Optional learning stage.
        """

        return None

    async def report(
        self,
        context: ExecutiveContext,
        result: ExecutiveResult,
    ) -> None:
        """
        Optional reporting stage.
        """

        return None