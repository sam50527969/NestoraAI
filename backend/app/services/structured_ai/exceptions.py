from __future__ import annotations


class StructuredAIError(Exception):
    """
    Base exception for all Structured AI Engine errors.
    """


class StructuredAIParseError(StructuredAIError):
    """
    Raised when the AI response cannot be parsed as valid JSON.
    """


class StructuredAIValidationError(StructuredAIError):
    """
    Raised when parsed JSON does not match the required Pydantic model.
    """


class StructuredAIRetryError(StructuredAIError):
    """
    Raised when all structured response attempts have failed.
    """