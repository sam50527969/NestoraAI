from __future__ import annotations

import json
from typing import Type, TypeVar

from pydantic import BaseModel

from app.services.llm import llm
from app.services.structured_ai.exceptions import (
    StructuredAIRetryError,
)
from app.services.structured_ai.parser import (
    StructuredAIParser,
)

T = TypeVar("T", bound=BaseModel)


class StructuredAIEngine:
    """
    Generates and validates structured AI responses.
    """

    def __init__(
        self,
        *,
        max_attempts: int = 2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1."
            )

        self.max_attempts = max_attempts
        self.parser = StructuredAIParser()

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
    ) -> T:
        schema = response_model.model_json_schema()

        structured_system_prompt = (
            f"{system_prompt.strip()}\n\n"
            "You must return only one valid JSON object.\n"
            "Do not use Markdown code fences.\n"
            "Do not include commentary before or after the JSON.\n"
            "The JSON must strictly match this schema:\n"
            f"{json.dumps(schema, indent=2)}"
        )

        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            attempt_prompt = user_prompt

            if attempt > 1:
                attempt_prompt = (
                    f"{user_prompt.strip()}\n\n"
                    "Your previous response was invalid. "
                    "Return corrected JSON only, matching the required schema."
                )

            try:
                response_text = await llm.generate(
                    system_prompt=structured_system_prompt,
                    user_prompt=attempt_prompt,
                )

                return self.parser.parse(
                    response_text=response_text,
                    response_model=response_model,
                )

            except Exception as exc:
                last_error = exc

        raise StructuredAIRetryError(
            "Structured AI generation failed after "
            f"{self.max_attempts} attempt(s). "
            f"Last error: {last_error}"
        )


structured_ai = StructuredAIEngine()