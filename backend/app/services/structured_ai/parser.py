from __future__ import annotations

import json
import re
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.services.structured_ai.exceptions import (
    StructuredAIParseError,
    StructuredAIValidationError,
)

T = TypeVar("T", bound=BaseModel)


class StructuredAIParser:
    """
    Parses and validates structured AI responses.
    """

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Extract JSON from raw AI output.

        Supports:
        - Plain JSON
        - ```json ... ```
        - ``` ... ```
        """

        text = text.strip()

        if text.startswith("{") and text.endswith("}"):
            return text

        match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

        raise StructuredAIParseError(
            "No JSON object could be found in the AI response."
        )

    @classmethod
    def parse(
        cls,
        *,
        response_text: str,
        response_model: Type[T],
    ) -> T:
        """
        Parse AI response into a validated Pydantic model.
        """

        try:
            json_text = cls._extract_json(response_text)
            data = json.loads(json_text)

        except json.JSONDecodeError as exc:
            raise StructuredAIParseError(
                f"Invalid JSON: {exc}"
            ) from exc

        except StructuredAIParseError:
            raise

        try:
            return response_model.model_validate(data)

        except ValidationError as exc:
            raise StructuredAIValidationError(
                str(exc)
            ) from exc