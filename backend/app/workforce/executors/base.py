from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type

from pydantic import BaseModel

from app.ai.gemini_provider import (
    GeminiConfigurationError,
    GeminiGenerationError,
    GeminiProvider,
)


class BaseExecutive(ABC):
    """
    Shared execution framework for all AI executives.
    """

    name: str = "Executive"
    response_model: Type[BaseModel]

    @property
    @abstractmethod
    def system_instruction(self) -> str:
        """System prompt supplied to Gemini."""
        ...

    @abstractmethod
    def build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:
        """Build the user prompt."""
        ...

    @abstractmethod
    def fallback_output(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
        error_message: str,
    ) -> dict[str, Any]:
        """Return deterministic fallback data."""
        ...

    def execute(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = self.build_prompt(
            title=title,
            description=description,
            input_data=input_data,
        )

        try:
            provider = GeminiProvider()

            report = provider.generate_structured(
                prompt=prompt,
                response_model=self.response_model,
                system_instruction=self.system_instruction,
            )

            result = report.model_dump()

            result["source_description"] = description
            result["input_data"] = input_data
            result["ai_provider"] = "Gemini"

            return result

        except (
            GeminiConfigurationError,
            GeminiGenerationError,
        ) as exc:

            return self.fallback_output(
                title=title,
                description=description,
                input_data=input_data,
                error_message=str(exc),
            )