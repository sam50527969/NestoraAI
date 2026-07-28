import os
from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError


ResponseModel = TypeVar(
    "ResponseModel",
    bound=BaseModel,
)


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini is not configured correctly."""


class GeminiGenerationError(RuntimeError):
    """Raised when Gemini cannot generate a valid response."""


class GeminiProvider:
    """
    Reusable Gemini provider for all Nestora AI executives.

    Every executive (Marketing, Finance, Sales, HR, Reception,
    Operations, etc.) will use this provider so AI integration
    remains centralized.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:

        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
        )

        self.model = (
            model
            or os.getenv(
                "GEMINI_MODEL",
                "gemini-3.5-flash",
            )
        )

        if not self.api_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY was not found in .env"
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def generate_structured(
        self,
        *,
        prompt: str,
        response_model: type[ResponseModel],
        system_instruction: str | None = None,
    ) -> ResponseModel:

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_model,
                ),
            )

        except Exception as exc:
            raise GeminiGenerationError(
                f"Gemini request failed: {exc}"
            ) from exc

        if not response.text:
            raise GeminiGenerationError(
                "Gemini returned an empty response."
            )

        try:
            return response_model.model_validate_json(
                response.text
            )

        except ValidationError as exc:
            raise GeminiGenerationError(
                "Gemini returned invalid structured JSON."
            ) from exc