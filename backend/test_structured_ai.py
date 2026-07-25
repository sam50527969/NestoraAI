from __future__ import annotations

import asyncio

from dotenv import load_dotenv

load_dotenv()

from app.executives.followup.schemas import FollowupRecommendation
from app.services.structured_ai import structured_ai


async def main() -> None:
    print("Testing Structured AI Engine...")

    try:
        recommendation = await structured_ai.generate(
            system_prompt=(
                "You are Nestora's AI Follow-up Executive. "
                "Analyze leads and recommend the best action to maximize conversion."
            ),
            user_prompt=(
                "Lead name: Ahmed Khan\n"
                "Business: Demo Dental Clinic\n"
                "Service: Dental Implant\n"
                "Status: New\n"
                "Source: WhatsApp\n"
                "Days since last contact: 0\n"
                "Notes: Requested an evening appointment."
            ),
            response_model=FollowupRecommendation,
        )

        print("\nSUCCESS: Structured response generated.")
        print("\nVALIDATED RESULT:")
        print(recommendation.model_dump_json(indent=2))

        print("\nPYTHON MODEL:")
        print(type(recommendation).__name__)

    except Exception as error:
        print("\nFAILED: Structured generation could not be completed.")
        print(f"\nERROR TYPE: {type(error).__name__}")
        print(f"ERROR DETAILS: {error}")


if __name__ == "__main__":
    asyncio.run(main())