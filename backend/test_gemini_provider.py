from __future__ import annotations

import asyncio

from dotenv import load_dotenv

# Load settings from backend/.env before importing the provider.
load_dotenv()

from app.services.llm.gemini import GeminiLLMProvider


async def main() -> None:
    print("Testing Gemini connection...")

    try:
        provider = GeminiLLMProvider()

        response = await provider.generate(
            system_prompt=(
                "You are the AI engine for Nestora AI Business OS. "
                "Respond clearly and briefly."
            ),
            user_prompt=(
                "Confirm that the Gemini provider is connected. "
                "Reply in one sentence."
            ),
        )

        print("\nSUCCESS: Gemini is connected.")
        print("\nGEMINI RESPONSE:")
        print(response)

    except Exception as error:
        print("\nFAILED: Gemini connection could not be completed.")
        print(f"\nERROR TYPE: {type(error).__name__}")
        print(f"ERROR DETAILS: {error}")


if __name__ == "__main__":
    asyncio.run(main())