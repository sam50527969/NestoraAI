from __future__ import annotations

import os

from google import genai
from google.genai import types

from app.services.llm.base import BaseLLMProvider


class GeminiLLMProvider(BaseLLMProvider):
    """
    Google Gemini implementation of Nestora's LLM provider interface.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key,
        )

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4,
            ),
        )

        text = response.text

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()