from __future__ import annotations


class ObjectiveError(Exception):
    """
    Base exception for all Objective Engine errors.
    """


class ObjectiveValidationError(ObjectiveError):
    """
    Raised when a business objective contains invalid
    or incomplete information.
    """


class BusinessProfileRequiredError(ObjectiveError):
    """
    Raised when objective analysis is attempted without
    a valid business profile.
    """


class ObjectiveAnalysisError(ObjectiveError):
    """
    Raised when the Objective Analyzer cannot complete
    its business analysis.
    """


class StrategyGenerationError(ObjectiveError):
    """
    Raised when the Strategist cannot produce a valid
    strategy recommendation.
    """


class ObjectiveExecutionError(ObjectiveError):
    """
    Raised when the Objective Engine cannot hand the
    approved strategy to the execution pipeline.
    """