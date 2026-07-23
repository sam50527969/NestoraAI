class ExecutiveError(Exception):
    """
    Base executive exception.
    """


class ExecutiveExecutionError(
    ExecutiveError,
):
    """
    Raised when execution fails.
    """


class ExecutiveValidationError(
    ExecutiveError,
):
    """
    Raised when context is invalid.
    """