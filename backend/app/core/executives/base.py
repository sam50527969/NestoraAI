from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.executives.context import ExecutiveContext
from app.core.executives.exceptions import ExecutiveValidationError
from app.core.executives.result import ExecutiveResult


class ExecutiveBase(ABC):
    """
    Base class for every Nestora executive.

    Every executive follows the same lifecycle:

    validate
        -> analyze
        -> plan
        -> execute
        -> learn
        -> report
    """

    def __init__(self) -> None:
        self.initialized = True

    async def run(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveResult:
        """
        Execute the complete executive lifecycle.
        """

        await self.validate(context)
        await self.analyze(context)
        await self.plan(context)

        result = await self.execute(context)

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
        Validate the supplied execution context.
        """

        if not isinstance(context, ExecutiveContext):
            raise ExecutiveValidationError(
                "Context must be an ExecutiveContext instance."
            )

        if not context.mission.strip():
            raise ExecutiveValidationError(
                "Mission cannot be empty."
            )

        if (
            context.objective is not None
            and not context.objective.strip()
        ):
            raise ExecutiveValidationError(
                "Objective cannot contain only whitespace."
            )

        if (
            context.business_id is not None
            and not context.business_id.strip()
        ):
            raise ExecutiveValidationError(
                "Business ID cannot contain only whitespace."
            )

        if (
            context.user_id is not None
            and not context.user_id.strip()
        ):
            raise ExecutiveValidationError(
                "User ID cannot contain only whitespace."
            )

    @abstractmethod
    async def analyze(
        self,
        context: ExecutiveContext,
    ) -> None:
        """
        Analyze the mission and available business context.
        """

        ...

    @abstractmethod
    async def plan(
        self,
        context: ExecutiveContext,
    ) -> None:
        """
        Prepare the executive's execution plan.
        """

        ...

    @abstractmethod
    async def execute(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveResult:
        """
        Perform the executive's assigned work.
        """

        ...

    async def learn(
        self,
        context: ExecutiveContext,
        result: ExecutiveResult,
    ) -> None:
        """
        Optional learning stage.

        Executives may override this method to store lessons,
        update memory, or improve future execution.
        """

        return None

    async def report(
        self,
        context: ExecutiveContext,
        result: ExecutiveResult,
    ) -> None:
        """
        Optional reporting stage.

        Executives may override this method to publish audit
        information, events, notifications, or summaries.
        """

        return None